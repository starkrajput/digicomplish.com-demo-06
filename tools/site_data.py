"""Single source of truth for the Services branch.

Pillar / service names, slugs, groups, card copy and build status live here.
The mega menu, the Services page cards, the Workforce & Talent service cards
and every holding page are generated from this file, so a rename here updates
all of them on the next build (`python tools/build_services.py`).

Set `built=True` on a page once its real page exists: the build then stops
writing a holding page at that address. Links never change, because they always
use the final URL.

Copy is taken verbatim from "Website Content: Services and Workforce & Talent
Pages" (7 Oct 2026). Do not add names, clients, logos, certifications or figures.
"""

SITE = "https://digicomplish.com"

# Form delivery. Leave empty until Digicomplish supplies the CRM / notification
# endpoint; while empty the form validates and confirms on the page only.
FORM_ENDPOINT = ""


def svc(name, slug, group=None, descriptor="", receive="", built=False):
    return dict(name=name, slug=slug, group=group, descriptor=descriptor,
                receive=receive, built=built)


PILLARS = [
    dict(
        name="Workforce & Talent", slug="workforce", built=True,
        summary="Workforce planning, talent intelligence, and workforce programs at enterprise scale.",
        featured=["strategic-workforce-planning", "rpo", "msp", "global-talent-sourcing"],
        featured_labels={"rpo": "Recruitment Process Outsourcing", "msp": "Managed Services Provider"},
        groups=[
            ("Workforce Advisory", "Define what you need before you hire."),
            ("Talent Intelligence", "Understand the market before you commit."),
            ("Enterprise Talent Solutions", "Run workforce programs at enterprise scale."),
        ],
        services=[
            svc("Strategic Workforce Planning", "strategic-workforce-planning", "Workforce Advisory",
                "Align headcount, skills and locations with business plans and budgets.",
                "a workforce plan with headcount, skills and location scenarios tied to your budget."),
            svc("Executive Search & Leadership Advisory", "executive-search", "Workforce Advisory",
                "Identify and assess senior leaders, and advise on the leadership profile the business requires.",
                "a written leadership profile and an assessed shortlist."),
            svc("Workforce Analytics", "workforce-analytics", "Talent Intelligence",
                "Turn hiring, attrition and cost data into decisions about capacity and spend.",
                "a written analysis and dashboard of hiring, attrition and cost drivers."),
            svc("AI-Enabled Talent Mapping", "talent-mapping", "Talent Intelligence",
                "Identify where specific skills sit, who employs them and what they cost, market by market.",
                "a market map of talent supply, employers and pay ranges by location."),
            svc("Skills & Capability Assessment", "skills-assessment", "Talent Intelligence",
                "Measure current skills against the skills your strategy requires.",
                "a skills inventory and a gap analysis against your plan."),
            svc("Recruitment Process Outsourcing (RPO)", "rpo", "Enterprise Talent Solutions",
                "Operating your hiring function end to end, against agreed service levels.",
                "a managed hiring function with agreed service levels and regular reporting."),
            svc("Managed Services Provider (MSP)", "msp", "Enterprise Talent Solutions",
                "Program management and vendor governance for your contingent workforce, operated on your existing systems.",
                "a governed contingent program with vendor oversight and consolidated spend reporting."),
            svc("Global Talent Sourcing", "global-talent-sourcing", "Enterprise Talent Solutions",
                "Talent strategy and sourcing across the markets your plan requires, for permanent and contract roles.",
                "a market-by-market sourcing plan and screened talent for each target market."),
            svc("On-Demand Technology Talent", "on-demand-technology-talent", "Enterprise Talent Solutions",
                "Technology specialists, vetted and matched to your team, on contract or contract-to-hire.",
                "specialists matched to your technology and team, in place on an agreed timeline."),
        ],
    ),
    dict(
        name="Global Capability Centers", slug="gcc", built=False,
        summary="Strategy, setup and scaling of a Global Capability Center (GCC) that operates as an extension of your organization.",
        featured=["advisory-setup", "build-operate-transfer", "capability-pods"],
        featured_labels={"build-operate-transfer": "Build-Operate-Transfer"},
        groups=[],
        services=[
            svc("GCC Advisory & Setup", "advisory-setup"),
            svc("Build-Operate-Transfer (BOT)", "build-operate-transfer"),
            svc("Dedicated Capability Pods", "capability-pods"),
        ],
    ),
    dict(
        name="Technology & AI", slug="technology", built=False,
        summary="Platform modernization, applied AI and custom software, tied to defined business outcomes.",
        featured=["erp", "enterprise-ai", "data-intelligence", "application-engineering"],
        featured_labels={},
        groups=[("Technology Advisory", ""), ("AI & Data Intelligence", ""), ("Enterprise Platform Solutions", "")],
        services=[
            svc("Technology & Operations Advisory", "advisory", "Technology Advisory"),
            svc("Cloud Strategy & Infrastructure", "cloud", "Technology Advisory"),
            svc("Enterprise AI & GenAI", "enterprise-ai", "AI & Data Intelligence"),
            svc("AI Agents & Intelligent Automation", "ai-agents", "AI & Data Intelligence"),
            svc("Data & Decision Intelligence", "data-intelligence", "AI & Data Intelligence"),
            svc("ERP Transformation", "erp", "Enterprise Platform Solutions"),
            svc("CRM & Customer Platforms", "crm", "Enterprise Platform Solutions"),
            svc("Custom Application Engineering", "application-engineering", "Enterprise Platform Solutions"),
        ],
    ),
]

HOW_WE_ENGAGE = dict(name="How We Engage", url="/how-we-engage/", built=False)


def pillar_url(p):
    return "/services/%s/" % p["slug"]


def service_url(p, s):
    return "/services/%s/%s/" % (p["slug"], s["slug"])


def find(slug, pillar_slug=None):
    """Look a service up by slug -> (pillar, service)."""
    for p in PILLARS:
        if pillar_slug and p["slug"] != pillar_slug:
            continue
        for s in p["services"]:
            if s["slug"] == slug:
                return p, s
    raise KeyError(slug)


# ---------------------------------------------------------------- page copy
# "Where to start": (title, [(link text, pillar slug, service slug or None)])
SERVICES_WHERE = [
    ("Building workforce capacity across markets.",
     [("Global Talent Sourcing", "workforce", "global-talent-sourcing"),
      ("Recruitment Process Outsourcing", "workforce", "rpo")]),
    ("Evaluating a capability center.",
     [("GCC Advisory & Setup", "gcc", "advisory-setup"),
      ("Build-Operate-Transfer", "gcc", "build-operate-transfer")]),
    ("Modernizing core systems.",
     [("ERP Transformation", "technology", "erp"),
      ("CRM & Customer Platforms", "technology", "crm")]),
    ("Applying AI to the business.",
     [("Enterprise AI & GenAI", "technology", "enterprise-ai"),
      ("AI Agents & Intelligent Automation", "technology", "ai-agents")]),
    ("Planning workforce and technology roadmaps.",
     [("Strategic Workforce Planning", "workforce", "strategic-workforce-planning"),
      ("Technology & Operations Advisory", "technology", "advisory")]),
]

WORKFORCE_WHERE = [
    ("Planning headcount, skills or an organizational change.",
     [("Strategic Workforce Planning", "workforce", "strategic-workforce-planning"),
      ("Workforce Analytics", "workforce", "workforce-analytics")]),
    ("Understanding a talent market or a skills gap.",
     [("AI-Enabled Talent Mapping", "workforce", "talent-mapping"),
      ("Skills & Capability Assessment", "workforce", "skills-assessment")]),
    ("Building workforce capacity across markets.",
     [("Global Talent Sourcing", "workforce", "global-talent-sourcing"),
      ("Recruitment Process Outsourcing", "workforce", "rpo"),
      ("On-Demand Technology Talent", "workforce", "on-demand-technology-talent")]),
    ("Strengthening senior leadership.",
     [("Executive Search & Leadership Advisory", "workforce", "executive-search")]),
    ("Governing contingent spend and vendors.",
     [("Managed Services Provider (MSP)", "workforce", "msp")]),
]

GLANCE = [("8+", "years in operation"), ("50+", "customers served"), ("3", "global locations")]

SERVICES_STEPS = [
    ("Understand", "We establish the business objective, the capabilities required, the timeline and the constraints with your leadership team."),
    ("Design", "We agree the operating model, the locations and the measures of success."),
    ("Deliver", "We run the program, either on your behalf or alongside your team."),
    ("Govern and improve", "We report against the agreed measures at a cadence set with your leadership team, and adjust the program as conditions change."),
]
WORKFORCE_STEPS = [
    ("Understand", "We establish the business objective, the roles and skills required, the timeline and the constraints with your leadership team."),
    ("Design", "We agree the operating model, the markets and locations, and the measures of success."),
    ("Deliver", "We run the program, either on your behalf or alongside your team."),
    ("Govern and improve", "We report against the agreed measures at a cadence set with your leadership team, and adjust the program as conditions change."),
]

SERVICES_APART = [
    ("Advice and delivery in one team.", "The people who plan the work also help deliver it, so plans are built to be executed."),
    ("Platform-neutral by design.", "We work within your existing systems and tools. You do not have to adopt, or migrate to, a new platform."),
    ("One consistent method.", "Technology, engineering, sales and executive work follow the same governed process, across industries."),
    ("Evidence before commitment.", "We use market and workforce intelligence to test each decision before budget is committed."),
    ("Senior ownership.", "Every engagement has a senior owner who is accountable for results and takes part in your leadership reviews."),
]
WORKFORCE_APART = [
    ("Workforce advice and delivery in one team.", "The people who plan the workforce also help deliver it, so the plan is built to be executed."),
    ("Platform-neutral by design.", "We run programs on your vendor management system and tools. You do not have to adopt, or migrate to, a new platform."),
    ("Evidence before commitment.", "Market and workforce intelligence tests each workforce decision before budget is committed."),
    ("Senior ownership.", "Every engagement has a senior owner who is accountable for results and takes part in your leadership reviews."),
]

ENGAGEMENT = [
    ("Advisory engagements.", "A defined question, answered by a senior team with a clear recommendation."),
    ("Managed programs.", "We run a function or program for you against agreed measures."),
    ("Outcome-based projects.", "Defined scope and deliverables under a statement of work."),
    ("Dedicated capability pods.", "A managed team that delivers agreed outcomes."),
    ("Build-Operate-Transfer.", "We build and run a capability, then transfer it to you."),
]

MEASURES = [
    "Capacity delivered against plan",
    "Quality of hire",
    "Early retention",
    "Cost against budget",
    "On contingent programs: vendor performance and compliance",
]
RISKS = [
    ("Worker engagement.", "The model is set around your requirements and the rules that apply in each market, and is documented in the contract before work begins."),
    ("Screening.", "Candidates are screened to your standards, with background checks where you require them."),
    ("Information security.", "Client and candidate information is handled under written confidentiality and data-handling controls."),
    ("Employment compliance.", "We follow the equal opportunity, pay transparency and employment rules that apply to each role and location."),
]
SCENARIOS = [
    ("Growth plans that outrun workforce capacity.",
     "Approved headcount spans several functions and the internal team cannot keep pace.",
     "A workforce plan and a delivery program run against agreed targets, with reporting on speed, quality and cost.",
     "One accountable program and a clear view of progress."),
    ("Contingent spend with no single owner.",
     "Contract workers arrive through many vendors, with inconsistent rates and no combined view.",
     "Governance and program management on the client's own systems.",
     "One view of spend, vendors and compliance."),
    ("Entering a new market without talent data.",
     "A new location or capability is planned without a view of local talent supply, competition and cost.",
     "Talent mapping and workforce analytics before any hiring begins.",
     "A location and capacity decision grounded in market evidence."),
]

FAQ = [
    ("How does Digicomplish differ from a typical recruitment vendor?",
     "We start with the workforce decision, not the requisition. Planning, market intelligence and delivery sit in one team, so the advice you receive is advice we are accountable for carrying out."),
    ("What is the difference between RPO and MSP?",
     "RPO takes on your hiring of employees. MSP governs your contingent workers and the vendors that supply them. The two are often combined."),
    ("Which industries do you serve?",
     "We work across industries. Our services are organized around capabilities such as hiring, workforce planning and contingent workforce management, and the same method applies to each."),
    ("Which engagement models do you support?",
     "Permanent, contract and contract-to-hire arrangements, set around your requirements and the rules of each market."),
    ("How do we start?",
     "A short conversation to understand the need, followed by a written proposal within five business days."),
]

# Insights. Each section renders only once enough articles are published:
# add {"title", "summary", "url"} dicts as the posts go live.
SERVICES_INSIGHTS = []       # shows the three most recent; hidden below 3
WORKFORCE_INSIGHTS = []      # the three planned articles; hidden until all 3 exist
WORKFORCE_PLANNED_INSIGHTS = [
    ("Sizing a workforce plan before hiring begins.", "How leadership teams set headcount, skills and locations against budget."),
    ("RPO or MSP: choosing the right model.", "What each governs, and when to use both."),
    ("Reading a talent market before you enter it.", "What supply, competition and cost reveal about where to hire."),
]

# Closing call to action: one shared block; heading and line per page.
CTA_SERVICES = ("Discuss your priorities with a senior member of our team.",
                "Tell us what you need to plan, build or run. We will reply within one business day.")
CTA_WORKFORCE = ("Discuss your workforce priorities with a senior member of our team.",
                 "Tell us what you need to plan, source or manage. We will reply within one business day.")

# 301 redirects (old -> new). Written to vercel.json and as static stubs.
REDIRECTS = [
    ("/services.html", "/services/"),
    ("/services/talent-fulfillment-solutions/", "/services/workforce/"),
    ("/talent-fulfillment-solutions.html", "/services/workforce/"),
    ("/services/digital-excellence/", "/services/technology/"),
    ("/digital-excellence.html", "/services/technology/"),
    ("/how-to-increase-your-youtube-subscribers.html", "/insights.html"),
    ("/how-to-get-the-most-out-of-your-press-release.html", "/insights.html"),
    ("/tips-for-remotely-managing-a-team.html", "/insights.html"),
    ("/industries/", "/index.html#industries"),
]
