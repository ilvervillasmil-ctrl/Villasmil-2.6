git clone https://github.com/ilvervillasmil-ctrl/Villasmil-2.6.git
cd Villasmil-2.6
git checkout -b feature/ci-fix

mkdir -p .github/workflows
cat > .github/workflows/test.yml <<'YAML'
# pega aquí exactamente el contenido del workflow que te pasé antes
YAML

mkdir -p villasmil_omega
cat > villasmil_omega/__init__.py <<'PY'
# Package init for villasmil_omega
__all__ = []
PY

git add .
git commit -m "CI: fix python matrix, skip editable install if no packaging metadata, add debug & PYTHONPATH"
git push -u origin feature/ci-fix
