#!/bin/zsh

# Script to compile the LaTeX paper to PDF

# Configuration
LATEX_SOURCE_DIR="docs/paper"
LATEX_MAIN_FILE="extended_abstract.tex"
OUTPUT_DIR="docs/paper"

# Ensure the output directory exists
mkdir -p "${OUTPUT_DIR}"

# Navigate to the source directory
cd "${LATEX_SOURCE_DIR}" || exit 1

# Compile the LaTeX document
# Run twice to ensure all references and ToC are correctly generated
pdflatex -output-directory="../paper" "${LATEX_MAIN_FILE}"
pdflatex -output-directory="../paper" "${LATEX_MAIN_FILE}"

# Clean up auxiliary files
# You can uncomment these lines if you want to remove .aux, .log, .out, .toc files
rm -f "../paper/${LATEX_MAIN_FILE%.tex}.aux"
rm -f "../paper/${LATEX_MAIN_FILE%.tex}.log"
rm -f "../paper/${LATEX_MAIN_FILE%.tex}.out"
rm -f "../paper/${LATEX_MAIN_FILE%.tex}.toc"
rm -f "../paper/${LATEX_MAIN_FILE%.tex}.nav"
rm -f "../paper/${LATEX_MAIN_FILE%.tex}.snm"
rm -f "../paper/${LATEX_MAIN_FILE%.tex}.bbl"
rm -f "../paper/${LATEX_MAIN_FILE%.tex}.blg"

# Navigate back to the original directory
cd - > /dev/null || exit 1

echo "PDF generated successfully in ${OUTPUT_DIR}/${LATEX_MAIN_FILE%.tex}.pdf"
