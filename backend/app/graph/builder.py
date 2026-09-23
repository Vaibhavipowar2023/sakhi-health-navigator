"""Langgraph builder - wires all agent nodes into the navigator graph"""

from langgraph.graph import StateGraph, END

from backend.app.agents.intake import extract_profile
from backend.app.agents.ranking import rank_providers
from backend.app.agents.research import (
    build_search_params, parse_mcp_results, parse_web_results,
    query_local_db, search_web,
)
from backend.app.agents.routing import route_patient
from backend.app.graph.state import NavigatorState
from backend.app.safety.red_flags import check_red_flags

# Nodes
def intake_node(state: NavigatorState) -> dict:
    profile = extract_profile(state.conversation)
    missing = profile.missing_required_fields()
    return {
        "profile": profile,
        "missing_fields": missing,
        "needs_more_info": len(missing) > 0,
    }


def safety_node(state: NavigatorState) -> dict:
    raw_text = " ".join(state.profile.symptoms)
    result = check_red_flags(raw_text, state.profile)

    flags = []
    if result.triggered:
        flags = [{"level": result.level, "rules": result.matched_rule_ids, "message": result.message}]

    # return updated profile with red_flags_detected set, don't mutate state directly
    updated_profile = state.profile.model_copy(
        update={"red_flags_detected": result.triggered},
    )

    return {
        "profile": updated_profile,
        "red_flags": flags,
        "crisis_detected": result.triggered,
    }


def routing_node(state: NavigatorState) -> dict:
    decision = route_patient(state.profile)
    return {"routing": decision}


def research_node(state: NavigatorState) -> dict:
    params = build_search_params(state.routing, state.profile.location)
    city = params["city"]
    specialty = params["specialty"]

    # pass symptoms so semantic search ranks providers by relevance
    symptoms_text = ", ".join(state.profile.symptoms) if state.profile.symptoms else ""
    raw_local = query_local_db(
        city=city,
        specialty=specialty,
        symptoms=symptoms_text,
    )

    if raw_local:
        # MongoDB has doctors in user's city, use those
        providers = parse_mcp_results(raw_local)
    else:
        # no doctors in user's city in MongoDB, search the web only
        raw_web = search_web(city, specialty, limit=5)
        providers = parse_web_results(raw_web)

    return {"providers": providers}


def ranking_node(state: NavigatorState) -> dict:
    ranked = rank_providers(
        state.providers,
        state.profile,
        state.routing.recommended_pathway,
    )
    return {"ranked": ranked}


# edges

def after_intake(state: NavigatorState) -> str:
    if state.needs_more_info:
        return "needs_info"
    return "continue"


def after_safety(state: NavigatorState) -> str:
    if state.crisis_detected:
        return "crisis"
    return "continue"


# --- graph ---

def build_graph() -> StateGraph:
    graph = StateGraph(NavigatorState)

    graph.add_node("intake", intake_node)
    graph.add_node("safety", safety_node)
    graph.add_node("routing", routing_node)
    graph.add_node("research", research_node)
    graph.add_node("ranking", ranking_node)

    graph.set_entry_point("intake")

    graph.add_conditional_edges("intake", after_intake, {
        "needs_info": END,
        "continue": "safety",
    })

    graph.add_conditional_edges("safety", after_safety, {
        "crisis": END,
        "continue": "routing",
    })

    graph.add_edge("routing", "research")
    graph.add_edge("research", "ranking")
    graph.add_edge("ranking", END)

    return graph.compile()
