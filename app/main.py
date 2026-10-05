from fastapi import FastAPI

from app.api.routes import (arguments, audit, classification, drafting, evidence, facts, issues,
                            jurisdiction, legal_analysis, maintainability, matters, precedents,
                            relief, review)

app = FastAPI(title="Company Matter Engine (HCD Company Bench)", version="0.1.0")
for module in (matters, facts, evidence, classification, jurisdiction, maintainability, legal_analysis,
               precedents, issues, arguments, relief, drafting, review, audit):
    app.include_router(module.router)


@app.get("/health")
def health():
    from app.core.versioning import current_versions
    return {"status": "ok", "versions": current_versions()}
