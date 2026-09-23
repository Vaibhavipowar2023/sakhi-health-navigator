import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import {
  Heart, Shield, MapPin, Clock, MessageCircle, Search,
  UserCheck, ArrowRight, CheckCircle, Star,
} from "lucide-react";
import Logo from "../components/Logo";

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: (i) => ({
    opacity: 1, y: 0,
    transition: { delay: i * 0.12, duration: 0.5, ease: "easeOut" },
  }),
};

const features = [
  {
    icon: Shield, title: "Safe Space",
    desc: "No judgments, no diagnosis. A caring guide to help you find the right specialist.",
    iconColor: "text-violet-600", bg: "bg-violet-50",
  },
  {
    icon: MapPin, title: "Nearby Doctors",
    desc: "Find women's health specialists in your city, ranked by what matters most to you.",
    iconColor: "text-emerald-600", bg: "bg-emerald-50",
  },
  {
    icon: Heart, title: "Women First",
    desc: "Built exclusively for women's health, from routine checkups to urgent care needs.",
    iconColor: "text-pink-600", bg: "bg-pink-50",
  },
  {
    icon: Clock, title: "Quick & Private",
    desc: "Describe your concerns in your own words. We'll find the right care in minutes.",
    iconColor: "text-amber-600", bg: "bg-amber-50",
  },
];

const steps = [
  { num: "1", title: "Tell us how you feel", desc: "Describe your symptoms in your own words, in any language.", icon: MessageCircle },
  { num: "2", title: "We find specialists", desc: "Our AI routes you to the best care pathway from 22+ specialties.", icon: Search },
  { num: "3", title: "Connect with a doctor", desc: "Get ranked results with contact info, ratings, and directions.", icon: UserCheck },
];

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-white">
      {/* navbar */}
      <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-gray-100">
        <div className="flex items-center justify-between px-6 py-3 max-w-6xl mx-auto">
          <div className="flex items-center gap-3">
            <Logo size={36} />
            <span className="text-xl font-bold bg-gradient-to-r from-violet-600 to-pink-500 bg-clip-text text-transparent">
              Sakhi
            </span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm text-gray-600">
            <a href="#how-it-works" className="hover:text-violet-600 transition-colors">How it works</a>
            <a href="#features" className="hover:text-violet-600 transition-colors">Features</a>
          </div>
          <button
            onClick={() => navigate("/chat")}
            className="px-5 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-violet-600 to-pink-500 rounded-full hover:shadow-lg hover:shadow-violet-200/50 transition-all duration-300"
          >
            Get Started
          </button>
        </div>
      </nav>

      {/* hero */}
      <section className="max-w-6xl mx-auto px-6 pt-12 pb-16 lg:pt-20 lg:pb-24 flex flex-col lg:flex-row items-center gap-12 lg:gap-16">
        <div className="flex-1 text-center lg:text-left">
          <motion.div
            className="inline-flex items-center gap-2 px-4 py-1.5 bg-violet-50 border border-violet-100 rounded-full text-sm text-violet-600 font-medium mb-6"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Heart className="w-4 h-4" /> Trusted by women across India
          </motion.div>

          <motion.h1
            className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 leading-[1.1] tracking-tight"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            Your Health,{" "}
            <span className="bg-gradient-to-r from-violet-600 to-pink-500 bg-clip-text text-transparent">
              Your Navigator
            </span>
          </motion.h1>

          <motion.p
            className="mt-6 text-lg text-gray-500 max-w-xl mx-auto lg:mx-0 leading-relaxed"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15, duration: 0.6 }}
          >
            Tell Sakhi how you're feeling. She'll guide you to the right specialist
            near you, with care, privacy, and zero judgment.
          </motion.p>

          <motion.div
            className="mt-8 flex flex-col sm:flex-row gap-4 justify-center lg:justify-start"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
          >
            <button
              onClick={() => navigate("/chat")}
              className="group px-8 py-4 text-white font-semibold bg-gradient-to-r from-violet-600 to-pink-500 rounded-full hover:shadow-xl hover:shadow-violet-200/50 transition-all duration-300 flex items-center justify-center gap-2"
            >
              Talk to Sakhi
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
            <a
              href="#how-it-works"
              className="px-8 py-4 font-semibold text-gray-700 bg-gray-50 border border-gray-200 rounded-full hover:bg-gray-100 transition-colors text-center"
            >
              See how it works
            </a>
          </motion.div>

          <motion.div
            className="mt-10 flex flex-wrap gap-4 justify-center lg:justify-start"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            {["No diagnosis", "No prescriptions", "100% private"].map((item) => (
              <div key={item} className="flex items-center gap-1.5 text-sm text-gray-500">
                <CheckCircle className="w-4 h-4 text-emerald-500" />
                <span>{item}</span>
              </div>
            ))}
          </motion.div>
        </div>

        {/* phone mockup */}
        <motion.div
          className="flex-1 flex justify-center"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.8, ease: "easeOut" }}
        >
          <div className="relative">
            <div className="absolute -top-12 -right-12 w-72 h-72 bg-violet-100 rounded-full blur-3xl opacity-60" />
            <div className="absolute -bottom-12 -left-12 w-56 h-56 bg-pink-100 rounded-full blur-3xl opacity-60" />

            <div className="relative w-[220px] sm:w-[260px] md:w-[280px] bg-gray-900 rounded-[3rem] p-3 shadow-2xl shadow-violet-900/20">
              <div className="absolute top-3 left-1/2 -translate-x-1/2 w-24 h-6 bg-gray-900 rounded-b-2xl z-10" />

              <div className="bg-gray-50 rounded-[2.3rem] overflow-hidden">
                <div className="bg-gradient-to-r from-violet-600 to-pink-500 px-5 pt-10 pb-3 flex items-center gap-2">
                  <div className="w-7 h-7 rounded-full bg-white/20 flex items-center justify-center">
                    <Heart className="w-3.5 h-3.5 text-white" />
                  </div>
                  <div>
                    <p className="text-white font-semibold text-xs">Sakhi</p>
                    <p className="text-violet-200 text-[9px]">Online</p>
                  </div>
                </div>

                <div className="px-3 py-3 space-y-2">
                  <div className="bg-white rounded-2xl rounded-bl-sm px-3 py-2 text-[10px] text-gray-700 w-fit max-w-[85%] shadow-sm">
                    Hi! Tell me what's going on, I'll find the right doctor for you.
                  </div>
                  <div className="bg-violet-500 text-white rounded-2xl rounded-br-sm px-3 py-2 text-[10px] ml-auto w-fit max-w-[85%]">
                    I've been having irregular periods
                  </div>
                  <div className="bg-white rounded-2xl rounded-bl-sm px-3 py-2 text-[10px] text-gray-700 w-fit max-w-[85%] shadow-sm">
                    Got it. What city are you in?
                  </div>
                  <div className="bg-violet-500 text-white rounded-2xl rounded-br-sm px-3 py-2 text-[10px] ml-auto w-fit max-w-[80%]">
                    Pune
                  </div>
                  <div className="bg-white rounded-2xl rounded-bl-sm px-3 py-2 text-[10px] text-gray-700 w-fit max-w-[85%] shadow-sm">
                    Found 20 gynecologists in Pune!
                  </div>
                  <div className="bg-white rounded-xl p-2 shadow-sm border border-gray-100 mx-1">
                    <div className="flex items-center gap-2">
                      <div className="w-5 h-5 rounded-full bg-violet-100 flex items-center justify-center">
                        <span className="text-[7px] font-bold text-violet-600">#1</span>
                      </div>
                      <div>
                        <p className="text-[9px] font-semibold text-gray-800">Dr. Priya Sharma</p>
                        <div className="flex items-center gap-0.5">
                          <Star className="w-2 h-2 text-amber-500 fill-amber-500" />
                          <span className="text-[8px] text-gray-500">4.8</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <motion.div
              className="absolute -top-3 -right-5 bg-white rounded-2xl shadow-lg shadow-pink-100 p-3 border border-pink-50"
              animate={{ y: [0, -8, 0] }}
              transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
            >
              <Heart className="w-5 h-5 text-pink-500" />
            </motion.div>
            <motion.div
              className="absolute top-1/3 -left-8 bg-white rounded-2xl shadow-lg shadow-violet-100 p-3 border border-violet-50"
              animate={{ y: [0, 8, 0] }}
              transition={{ duration: 4, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
            >
              <MapPin className="w-5 h-5 text-violet-500" />
            </motion.div>
            <motion.div
              className="absolute -bottom-3 -right-6 bg-white rounded-2xl shadow-lg shadow-emerald-100 p-3 border border-emerald-50"
              animate={{ y: [0, -6, 0] }}
              transition={{ duration: 3.5, repeat: Infinity, ease: "easeInOut", delay: 1 }}
            >
              <Shield className="w-5 h-5 text-emerald-500" />
            </motion.div>
          </div>
        </motion.div>
      </section>

      {/* stats */}
      <section className="bg-gray-50 border-y border-gray-100">
        <div className="max-w-6xl mx-auto px-6 py-10 grid grid-cols-3 gap-6 text-center">
          {[
            { num: "22+", label: "Care Pathways" },
            { num: "100%", label: "Private & Secure" },
            { num: "3", label: "Languages" },
          ].map((stat) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
            >
              <p className="text-2xl sm:text-3xl md:text-4xl font-bold bg-gradient-to-r from-violet-600 to-pink-500 bg-clip-text text-transparent">
                {stat.num}
              </p>
              <p className="text-xs sm:text-sm text-gray-500 mt-1">{stat.label}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* how it works */}
      <section id="how-it-works" className="max-w-6xl mx-auto px-6 py-16 lg:py-20">
        <motion.div
          className="text-center mb-14"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <p className="text-sm font-semibold text-violet-600 uppercase tracking-wider mb-3">Simple & Quick</p>
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900">How Sakhi Works</h2>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8 relative">
          <div className="hidden md:block absolute top-16 left-[20%] right-[20%] h-0.5 bg-gradient-to-r from-violet-200 via-pink-200 to-violet-200" />

          {steps.map((step, i) => (
            <motion.div
              key={step.num}
              className="text-center relative"
              custom={i}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={fadeUp}
            >
              <div className="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center mb-5 relative z-10 shadow-lg shadow-violet-200/50">
                <step.icon className="w-6 h-6 text-white" />
              </div>
              <span className="inline-block text-xs font-bold text-violet-600 bg-violet-50 px-3 py-1 rounded-full mb-3">
                Step {step.num}
              </span>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{step.title}</h3>
              <p className="text-sm text-gray-500 leading-relaxed max-w-xs mx-auto">{step.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* features */}
      <section id="features" className="bg-gray-50 py-16 lg:py-20">
        <div className="max-w-6xl mx-auto px-6">
          <motion.div
            className="text-center mb-14"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <p className="text-sm font-semibold text-violet-600 uppercase tracking-wider mb-3">Why Choose Sakhi</p>
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900">Built for Your Wellbeing</h2>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((f, i) => (
              <motion.div
                key={f.title}
                className="bg-white rounded-2xl p-6 border border-gray-100 hover:shadow-xl hover:shadow-violet-100/50 hover:-translate-y-1 transition-all duration-300"
                custom={i}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                variants={fadeUp}
              >
                <div className={`w-12 h-12 rounded-xl ${f.bg} flex items-center justify-center mb-4`}>
                  <f.icon className={`w-6 h-6 ${f.iconColor}`} />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">{f.title}</h3>
                <p className="text-sm text-gray-500 leading-relaxed">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="max-w-5xl mx-auto px-6 py-16 lg:py-20">
        <motion.div
          className="relative overflow-hidden bg-gradient-to-r from-violet-600 to-pink-500 rounded-3xl p-10 md:p-16 text-center"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <div className="absolute top-0 right-0 w-40 h-40 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2" />
          <div className="absolute bottom-0 left-0 w-32 h-32 bg-white/10 rounded-full translate-y-1/2 -translate-x-1/2" />

          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4 relative">
            Ready to Take the First Step?
          </h2>
          <p className="text-violet-100 mb-8 max-w-lg mx-auto relative">
            No sign ups, no personal data stored. Just tell Sakhi how you're feeling
            and she'll help you find the right care.
          </p>
          <button
            onClick={() => navigate("/chat")}
            className="group relative px-10 py-4 bg-white text-violet-600 font-bold rounded-full hover:shadow-xl transition-all duration-300 inline-flex items-center gap-2"
          >
            Start Now
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </button>
        </motion.div>
      </section>

      {/* footer */}
      <footer className="border-t border-gray-100 py-10 px-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Logo size={24} />
            <span className="text-sm font-semibold text-gray-700">Sakhi Health Navigator</span>
          </div>
          <p className="text-xs text-gray-400 text-center">
            Not a medical service. Does not diagnose or prescribe.
          </p>
          <p className="text-xs text-gray-400">&copy; {new Date().getFullYear()} Sakhi</p>
        </div>
      </footer>
    </div>
  );
}
