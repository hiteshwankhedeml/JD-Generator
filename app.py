import streamlit as st
import uuid
from typing import List, Optional
from pydantic import BaseModel, Field, ValidationError

# =========================================================
# Pydantic Models (Phase 2)
# =========================================================

class StructuredInput(BaseModel):
    education: str
    experience: int
    skills: str
    functional_area: str

    class Config:
        extra = "forbid"


class ExistingJDInput(BaseModel):
    existing_jd: str

    class Config:
        extra = "forbid"


class JDOutput(BaseModel):
    Education: str
    Experience: str
    Skills: List[str]
    RolesAndResponsibilities: List[str]

    class Config:
        extra = "forbid"


class SessionStateModel(BaseModel):
    session_id: str
    input_mode: str
    temperature: float
    base_inputs: dict

    class Config:
        extra = "forbid"


# =========================================================
# Session Helpers
# =========================================================

def init_session():
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.input_mode = None
    st.session_state.base_inputs = {}
    st.session_state.temperature = 0.7
    st.session_state.instructions = []
    st.session_state.instruction_summary = ""
    st.session_state.jd_versions = []


def hard_reset():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session()


if "session_id" not in st.session_state:
    init_session()


# =========================================================
# UI
# =========================================================

st.title("JD Generator – Phase 2 (State + Pydantic)")
st.caption(f"Session ID: {st.session_state.session_id}")

existing_jd = st.text_area(
    "Existing JD (optional)",
    height=150
)

education = st.selectbox(
    "Education Level",
    ["", "Graduate", "Post Graduate", "PhD"],
    disabled=bool(existing_jd.strip())
)

experience = st.slider(
    "Experience (Years)",
    0, 30, 0,
    disabled=bool(existing_jd.strip())
)

skills = st.text_input(
    "Skills (comma separated)",
    disabled=bool(existing_jd.strip())
)

functional_area = st.text_input(
    "Functional Area",
    disabled=bool(existing_jd.strip())
)

temperature = st.slider(
    "Temperature",
    0.0, 1.0,
    st.session_state.temperature
)

# =========================================================
# Detect Input Change → Hard Reset
# =========================================================

current_inputs = {
    "existing_jd": existing_jd.strip(),
    "education": education,
    "experience": experience,
    "skills": skills.strip(),
    "functional_area": functional_area.strip(),
}

previous_inputs = st.session_state.get("base_inputs")

if previous_inputs and current_inputs != previous_inputs:
    hard_reset()

# =========================================================
# Determine Mode
# =========================================================

if existing_jd.strip():
    st.session_state.input_mode = "EXISTING_JD"
else:
    st.session_state.input_mode = "STRUCTURED"

st.session_state.base_inputs = current_inputs
st.session_state.temperature = temperature

# =========================================================
# Validation using Pydantic (Phase 2)
# =========================================================

def validate_inputs():
    if st.session_state.input_mode == "STRUCTURED":
        StructuredInput(
            education=education,
            experience=experience,
            skills=skills.strip(),
            functional_area=functional_area.strip()
        )
    else:
        ExistingJDInput(
            existing_jd=existing_jd.strip()
        )

    SessionStateModel(
        session_id=st.session_state.session_id,
        input_mode=st.session_state.input_mode,
        temperature=st.session_state.temperature,
        base_inputs=st.session_state.base_inputs
    )


# =========================================================
# Action
# =========================================================

if st.button("Start / Generate JD (No LLM yet)"):
    try:
        validate_inputs()
        st.success("Phase 2 successful: Inputs validated via Pydantic.")
    except ValidationError as e:
        st.error("Input validation failed.")
        st.json(e.errors())

# =========================================================
# Debug
# =========================================================

with st.expander("Debug: Session State"):
    st.json(dict(st.session_state))
