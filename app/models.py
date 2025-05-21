from sentence_transformers import SentenceTransformer

# ──────────────────────────────  ANCHORS  ──────────────────────────────
# Set of high-level section headings that start "anchor mode".
ANCHORS: set[str] = {
    # Classic full Methods headers
    "materials and methods",
    "methods and materials",
    "methods",
    "methodology",
    "experimental procedures",
    "experimental section",
    "laboratory methods",
    "investigational methods",

    # Study / protocol level
    "study design",
    "research design",
    "methodological framework",
    "study protocol",
    "clinical protocol",
    "protocol",

    # Materials-only or split variants
    "materials",
    "materials, subjects and methods",
}

# ──────────────────────────  STOP-SECTION HEADS  ───────────────────────
# When any of these appears, capture stops.
STOPWORDS: set[str] = {
    "results",
    "discussion",
    "conclusion",
    "references",
    "introduction",
    "acknowledgements",
    "supplementary material",
    "supporting information",
    "appendix",
    "data availability",
    "conflict of interest",
    "author contributions",
    "conclusions"
}

METHOD_KEYWORDS: set[str] = {
    # General lab actions
    "purified", "purification", "clone", "cloning", "plasmid", "vector",
    "transfect", "transfection", "incubate", "centrifuge", "lysis",
    "assay", "culture", "strain", "buffer", "elution", "protein",
    "expression", "construct", "sequence", "inoculation", "growth media",
    "induction", "extraction", "quantification", "optimization", "reagent"

    # Extended expression and purification
    "expressed", "induced", "cleaved", "filtration", "folding", "refolding",
    "inclusion bodies", "elution", "polishing", "promoter", "column",
    "tag", "fusion", "media", "od600",

    # Analytical and structural biology
    "analysis", "mass spectrometry", "spectrometry", "ms analysis",
    "protein purification", "affinity purification", "chromatography", 
    "gel filtration", "western blot", "immunoblot", "sds-page",
    "pcr amplification", "rt-pcr", "qpcr", "sequencing", 
    "next-generation sequencing", "rna-seq", "microscopy", 
    "electron microscopy", "confocal microscopy", "crystallization", 
    "x-ray crystallography", "reagents",

    # Advanced bioanalytical techniques
    "maldi-tof", "esi-ms", "lc-ms", "ms/ms", "uv-vis", "cd spectroscopy",
    "fluorescence spectroscopy", "ftir", "raman spectroscopy", "nmr spectroscopy",
    "sec", "hplc", "hic", "sec-mals", "dls", "auc", "dsf",

    # Functional assays
    "enzyme activity assay", "cell proliferation", "cytotoxicity",
    "reporter assay", "inhibition assay", "ligand binding", "elisa",
    "flow cytometry", "immunoprecipitation",
}


ABSTRACT_ALTERNATES = {"introduction", "background", "overview", "summary"}
RESULTS_STOPWORDS = { "material","methods","conclusion", "references", "acknowledgements","conclusions"}
DISCUSSION_STOPWORDS = { "material","methods","conclusion", "references", "acknowledgements","conclusions"}
RESULTS_DISCUSSION_ANCHORS = {
    "results and discussion", "discussion and results", "results/discussion", "results & discussion",    "results",
    "findings",
    "experimental results",
    "observations",
    "experimental findings",
    "research results",     "discussion",
    "interpretation",
    "implications",
}

# ─────────────────────────────  Shared resources  ──────────────────────
MODEL = SentenceTransformer("all-MiniLM-L6-v2")
NS = {"tei": "http://www.tei-c.org/ns/1.0"}
GROBID_URL = "http://grobid:8070/api/processFulltextDocument"
