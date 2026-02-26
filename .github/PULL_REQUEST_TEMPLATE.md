## Team Number: T066

## Description
This PR upgrades the RAG (Retrieval-Augmented Generation) system to support multi-format knowledge ingestion. Previously, the bot was limited to a single hardcoded text file. This enhancement allows the bot to dynamically read, chunk, and index all `.txt` and `.pdf` files within the data directory, significantly expanding its "roast knowledge" capabilities.

## Related Issue
Closes #[INSERT NEW ISSUE NUMBER HERE] 
*(Note: If a new issue number wasn't assigned yet, write "Implemented as an enhancement request via Rule #14")*

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [x] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Code refactoring
- [x] Performance improvement
- [ ] Style/UI improvement

## Changes Made
- **Directory Loading:** Implemented `get_text_from_files()` in `rag.py` to iterate through the `/data` folder using `os.listdir`.
- **PDF Integration:** Added `PyPDF2` support to extract text from binary PDF files.
- **Dynamic Indexing:** Refactored `load_and_chunk()` to aggregate text from all supported files before building the FAISS vector index.
- **Dependencies:** Updated `requirements.txt` to include `PyPDF2`.
- **Security:** Verified that `.env` and sensitive keys are excluded from the repository tracking.

## Screenshots (if applicable)
<!-- You can paste the screenshot of the bot responding to the "Syntax Error" PDF roast here -->

## Testing
- [x] Verified that the bot successfully retrieves context from a `.pdf` file.
- [x] Verified that the bot still retrieves context from the original `.txt` file simultaneously.
- [x] Tested with multiple files in the `/data` directory to ensure FAISS index builds correctly.
- [x] No console errors or warnings during text extraction.

## Checklist
- [x] My code follows the project's code style guidelines
- [x] I have performed a self-review of my code
- [x] I have commented my code where necessary
- [x] My changes generate no new warnings
- [x] I have tested my changes thoroughly
- [x] I have read and followed the [CONTRIBUTING.md](CONTRIBUTING.md) guidelines

## Additional Notes
This feature was implemented to fulfill "Step 2" of the RAG bot evolution, moving from static file reading to a scalable directory-based knowledge base.