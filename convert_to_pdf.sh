#!/bin/bash
# Script de conversion Markdown vers PDF
# Utilisation: ./convert_to_pdf.sh

echo "🔄 Conversion du compte rendu en PDF..."

# Vérifier si pandoc est installé
if command -v pandoc &> /dev/null; then
    echo "✓ Pandoc trouvé - Conversion avec Pandoc"
    pandoc COMPTE_RENDU_TP_AIRFLOW.md \
        -o COMPTE_RENDU_TP_AIRFLOW.pdf \
        --pdf-engine=xelatex \
        -V geometry:margin=2cm \
        -V fontsize=11pt \
        -V documentclass=article \
        --toc \
        --toc-depth=3 \
        --highlight-style=tango
    echo "✅ PDF généré: COMPTE_RENDU_TP_AIRFLOW.pdf"
    
elif command -v markdown-pdf &> /dev/null; then
    echo "✓ markdown-pdf trouvé"
    markdown-pdf COMPTE_RENDU_TP_AIRFLOW.md
    echo "✅ PDF généré: COMPTE_RENDU_TP_AIRFLOW.pdf"
    
else
    echo "❌ Aucun outil de conversion trouvé!"
    echo ""
    echo "📋 Options pour convertir en PDF:"
    echo ""
    echo "Option 1 - Installer Pandoc (recommandé):"
    echo "  sudo apt-get install pandoc texlive-xetex texlive-fonts-recommended"
    echo "  puis: ./convert_to_pdf.sh"
    echo ""
    echo "Option 2 - Utiliser VS Code:"
    echo "  1. Installer l'extension 'Markdown PDF'"
    echo "  2. Ouvrir COMPTE_RENDU_TP_AIRFLOW.md"
    echo "  3. Clic droit → 'Markdown PDF: Export (pdf)'"
    echo ""
    echo "Option 3 - En ligne:"
    echo "  1. Ouvrir https://www.markdowntopdf.com/"
    echo "  2. Charger le fichier COMPTE_RENDU_TP_AIRFLOW.md"
    echo "  3. Télécharger le PDF"
    echo ""
    echo "Option 4 - Avec LibreOffice:"
    echo "  1. Ouvrir le fichier .md dans un éditeur de texte"
    echo "  2. Copier le contenu"
    echo "  3. Coller dans LibreOffice Writer"
    echo "  4. Exporter en PDF"
    echo ""
    exit 1
fi
