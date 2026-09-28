import os
import tempfile

import requests
import streamlit as st

from dotenv import load_dotenv

from backend.services.document_service import (
    format_docx,
    format_pdf,
    format_txt,
)

from backend.utils.text_utils import (
    escape_html
)


load_dotenv()


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


st.set_page_config(

    page_title="LegalEase",

    page_icon="⚖️",

    layout="wide",
)


st.markdown(
    """
    <style>

    .hero {
        padding: 1.5rem;
        border-radius: 16px;
        background: #101828;
        color: white;
        margin-bottom: 1rem;
    }

    .preview {
        background: #0b1220;
        color: #e5e7eb;
        padding: 1.2rem;
        border-radius: 14px;
        min-height: 500px;
        max-height: 700px;
        overflow-y: auto;
        white-space: pre-wrap;
        font-family: Georgia, serif;
        line-height: 1.65;
    }

    .notice {
        padding: .75rem 1rem;
        border-left: 4px solid #64748b;
        background: #f8fafc;
        border-radius: 6px;
        margin: .75rem 0;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:

    st.header("⚖️ LegalEase")

    st.caption(
        "AI-powered legal document drafting"
    )

    try:

        response = requests.get(
            f"{BACKEND_URL}/health",
            timeout=4
        )

        if response.ok:

            data = response.json()

            st.write(
                "**Backend:** Connected"
            )

            if data.get("ai_configured"):

                st.write(
                    "**Gemini:** Configured"
                )

            else:

                st.write(
                    "**Gemini:** Not configured"
                )

        else:

            st.write(
                f"**Backend:** Error {response.status_code}"
            )

    except requests.RequestException:

        st.write(
            "**Backend:** Unavailable"
        )

    st.divider()

    st.caption(
        "Review AI output before use."
    )


st.markdown(
    """
    <div class="hero">

    <h1>LegalEase</h1>

    <p>
    Create editable legal-document drafts
    with AI and export them as TXT, DOCX or PDF.
    </p>

    </div>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class="notice">

    <b>Important:</b>

    AI-assisted drafts are not legal advice.
    Verify the document for your jurisdiction
    and circumstances.

    </div>
    """,
    unsafe_allow_html=True,
)


document_types = [

    "Employment Contract",

    "Non-Disclosure Agreement",

    "Lease Agreement",

    "Employment Offer Letter",

    "Freelance Work Contract",

    "Service Agreement",

    "General Agreement",

    "Custom",
]


with st.form("legal_form"):

    column1, column2 = st.columns(2)

    with column1:

        selected_type = st.selectbox(
            "Document type",
            document_types
        )

        if selected_type == "Custom":

            document_type = st.text_input(
                "Custom document type",
                placeholder=(
                    "e.g. Consulting Agreement"
                )
            )

        else:

            document_type = selected_type

        effective_date = st.date_input(
            "Effective date"
        )

        jurisdiction = st.text_input(
            "Jurisdiction",
            placeholder=(
                "e.g. Tamil Nadu, India"
            )
        )

    with column2:

        parties = st.text_area(

            "Parties involved",

            height=120,

            placeholder=(
                "Jane Doe (Provider); "
                "ABC Corporation (Client)"
            ),
        )

        terms = st.text_area(

            "Terms & conditions",

            height=180,

            placeholder=(
                "Payment within 30 days; "
                "Confidentiality applies; "
                "Either party may terminate "
                "with 15 days notice"
            ),
        )

    additional_instructions = st.text_area(

        "Additional instructions (optional)",

        height=100,

        placeholder=(
            "Add specific drafting instructions."
        ),
    )

    logo = st.file_uploader(

        "Optional logo",

        type=[
            "png",
            "jpg",
            "jpeg"
        ],
    )

    submitted = st.form_submit_button(

        "✨ Generate Document",

        type="primary",

        use_container_width=True,
    )


if submitted:

    if (
        not document_type.strip()
        or not parties.strip()
        or not terms.strip()
    ):

        st.error(
            "Please complete document type, "
            "parties and terms."
        )

    else:

        payload = {

            "document_type":
                document_type.strip(),

            "parties":
                parties.strip(),

            "terms":
                terms.strip(),

            "effective_date":
                effective_date.isoformat(),

            "jurisdiction":
                jurisdiction.strip()
                or "Not specified",

            "additional_instructions":
                additional_instructions.strip(),
        }

        try:

            with st.spinner(
                "Generating your document..."
            ):

                response = requests.post(

                    f"{BACKEND_URL}/generate",

                    json=payload,

                    timeout=120,
                )

            if response.ok:

                result = response.json()

                st.session_state[
                    "document"
                ] = result["content"]

                st.session_state[
                    "document_type"
                ] = result["document_type"]

                st.session_state[
                    "model"
                ] = result["model"]

                st.success(
                    "Document generated successfully."
                )

            else:

                try:

                    detail = response.json().get(
                        "detail",
                        response.text
                    )

                except ValueError:

                    detail = response.text

                st.error(
                    f"Generation failed: {detail}"
                )

        except requests.RequestException as exc:

            st.error(
                f"Could not connect to FastAPI: {exc}"
            )


if "document" in st.session_state:

    st.divider()

    st.subheader(
        "Document Preview & Editor"
    )

    edited_document = st.text_area(

        "Edit the generated document",

        value=st.session_state["document"],

        height=650,
    )

    st.session_state[
        "document"
    ] = edited_document

    left, right = st.columns(
        [2, 1]
    )

    with left:

        st.markdown(
            "**Rendered preview**"
        )

        st.markdown(

            f"""
            <div class="preview">

            {escape_html(edited_document)}

            </div>
            """,

            unsafe_allow_html=True,
        )

    with right:

        st.markdown(
            "**Export**"
        )

        doc_type = st.session_state[
            "document_type"
        ]

        if logo:

            logo_bytes = logo.getvalue()

        else:

            logo_bytes = None

        txt_bytes = format_txt(
            edited_document
        )

        docx_bytes = format_docx(

            edited_document,

            doc_type,

            logo_bytes
        )

        logo_path = None

        if logo_bytes:

            suffix = (
                ".png"
                if (logo.type or "").endswith("png")
                else ".jpg"
            )

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix
            ) as temporary_file:

                temporary_file.write(
                    logo_bytes
                )

                logo_path = (
                    temporary_file.name
                )

        try:

            pdf_bytes = format_pdf(

                edited_document,

                doc_type,

                logo_path
            )

        finally:

            if logo_path:

                try:

                    os.unlink(
                        logo_path
                    )

                except OSError:

                    pass

        safe_name = "".join(

            character
            if character.isalnum()
            else "_"

            for character in doc_type

        ).strip("_")

        if not safe_name:

            safe_name = (
                "legal_document"
            )

        st.download_button(

            "⬇️ Download TXT",

            data=txt_bytes,

            file_name=(
                f"{safe_name}.txt"
            ),

            mime="text/plain",

            use_container_width=True,
        )

        st.download_button(

            "⬇️ Download DOCX",

            data=docx_bytes,

            file_name=(
                f"{safe_name}.docx"
            ),

            mime=(
                "application/"
                "vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),

            use_container_width=True,
        )

        st.download_button(

            "⬇️ Download PDF",

            data=pdf_bytes,

            file_name=(
                f"{safe_name}.pdf"
            ),

            mime="application/pdf",

            use_container_width=True,
        )

        st.caption(

            f"Model: "
            f"{st.session_state.get(
                'model',
                'configured Gemini model'
            )}"

        )