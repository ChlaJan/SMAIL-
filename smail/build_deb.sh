#!/usr/bin/env bash
# =============================================================================
# build_deb.sh — Package 'smail' as a .deb (Poetry project)
# =============================================================================

set -euo pipefail

APP_NAME="smail"
APP_VERSION="0.1.8"
APP_DESCRIPTION="smail email client"
APP_MAINTAINER="Chladek Jan <253185@vutbr.cz>"
BIN_NAME="smail"
INSTALL_PREFIX="/opt/${APP_NAME}"
ARCH="amd64"

# PyQt5 from pip bundles its own Qt5 — so we do NOT list libqt5* here.
# We DO need xcb/gl/dbus system libs that PyQt5 loads at runtime.
DEB_DEPENDS="\
python3.12, \
libgl1, \
libegl1, \
libdbus-1-3, \
libxcb-icccm4, \
libxcb-image0, \
libxcb-keysyms1, \
libxcb-randr0, \
libxcb-render-util0, \
libxcb-xinerama0, \
libxcb-xkb1, \
libxkbcommon-x11-0, \
libxrandr2"

SCONF_DIR="$(realpath ../sconf)"
# ---------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${SCRIPT_DIR}/deb_build"
PKG_ROOT="${BUILD_DIR}/${APP_NAME}_${APP_VERSION}"
VENV_DIR="${PKG_ROOT}${INSTALL_PREFIX}"
DEBIAN_DIR="${PKG_ROOT}/DEBIAN"
BIN_DIR="${PKG_ROOT}/usr/local/bin"

# ---------------------------------------------------------------------------
echo "==> Checking prerequisites..."
[ -d "${SCONF_DIR}" ] || { echo "ERROR: sconf not found at ${SCONF_DIR}"; exit 1; }
for cmd in poetry python3.12 dpkg-deb; do
  command -v "$cmd" &>/dev/null || { echo "ERROR: '$cmd' not found"; exit 1; }
done

# ---------------------------------------------------------------------------
echo "==> Cleaning previous build..."
rm -rf "${BUILD_DIR}"
mkdir -p "${DEBIAN_DIR}" "${BIN_DIR}" "${VENV_DIR}"

# ---------------------------------------------------------------------------
echo "==> Building sconf wheel..."
SCONF_DIST="${BUILD_DIR}/sconf_dist"
mkdir -p "${SCONF_DIST}"
(cd "${SCONF_DIR}" && poetry build --format wheel --output "${SCONF_DIST}" -q)
SCONF_WHEEL=$(ls "${SCONF_DIST}"/*.whl | sort -V | tail -n1)

# ---------------------------------------------------------------------------
echo "==> Exporting requirements (excluding sconf)..."
poetry export \
  --format requirements.txt \
  --output "${BUILD_DIR}/requirements.txt" \
  --without-hashes
sed -i '/sconf/Id' "${BUILD_DIR}/requirements.txt"

# ---------------------------------------------------------------------------
echo "==> Building smail wheel..."
poetry build --format wheel -q
SMAIL_WHEEL=$(ls "${SCRIPT_DIR}/dist/smail-"*.whl | sort -V | tail -n1)

# ---------------------------------------------------------------------------
echo "==> Creating python3.12 virtualenv..."
python3.12 -m venv "${VENV_DIR}"
PIP="${VENV_DIR}/bin/pip"
"${PIP}" install --quiet --upgrade pip

echo "==> Purging pip cache (avoids corrupted cache errors)..."
"${PIP}" cache purge || true

"${PIP}" install --quiet --require-virtualenv -r "${BUILD_DIR}/requirements.txt"
"${PIP}" install --quiet --require-virtualenv "${SCONF_WHEEL}"
"${PIP}" install --quiet --require-virtualenv "${SMAIL_WHEEL}"

# ---------------------------------------------------------------------------
# Patch text-based shebang lines
echo "==> Patching venv text files..."
find "${VENV_DIR}/bin" -type f | while read -r f; do
  if file "$f" 2>/dev/null | grep -q "text"; then
    sed -i "s|${VENV_DIR}|${INSTALL_PREFIX}|g" "$f"
  fi
done
sed -i "s|${VENV_DIR}|${INSTALL_PREFIX}|g" "${VENV_DIR}/pyvenv.cfg"

# Recreate python symlinks so they work on the TARGET machine
# (original symlinks point to the build machine's python3.12 path)
echo "==> Recreating python symlinks..."
(
  cd "${VENV_DIR}/bin"
  rm -f python python3 python3.12
  # These will resolve against the system Python on the target machine
  ln -s /usr/bin/python3.12 python3.12
  ln -s python3.12 python3
  ln -s python3.12 python
)

# ---------------------------------------------------------------------------
echo "==> Writing launcher /usr/local/bin/${BIN_NAME}..."
mkdir -p "${BIN_DIR}"
cat > "${BIN_DIR}/${BIN_NAME}" <<EOF
#!/bin/bash
exec "${INSTALL_PREFIX}/bin/python3.12" -m smail "\$@"
EOF
chmod 0755 "${BIN_DIR}/${BIN_NAME}"
[ -f "${BIN_DIR}/${BIN_NAME}" ] || { echo "ERROR: failed to write launcher"; exit 1; }
echo "    OK: $(ls -la "${BIN_DIR}/${BIN_NAME}")"

# ---------------------------------------------------------------------------
INSTALLED_SIZE=$(du -sk "${PKG_ROOT}" | awk '{print $1}')
echo "==> Writing DEBIAN/control..."
cat > "${DEBIAN_DIR}/control" <<EOF
Package: ${APP_NAME}
Version: ${APP_VERSION}
Architecture: ${ARCH}
Maintainer: ${APP_MAINTAINER}
Installed-Size: ${INSTALLED_SIZE}
Depends: ${DEB_DEPENDS}
Description: ${APP_DESCRIPTION}
EOF

# ---------------------------------------------------------------------------
# postinst: ensure Qt xcb platform plugin can be found
cat > "${DEBIAN_DIR}/postinst" <<EOF
#!/bin/bash
set -e
echo "smail installed. Run with: smail"

# On headless or minimal systems, Qt needs this env var
# (already set in the launcher, but inform the user)
if [ ! -e /usr/lib/x86_64-linux-gnu/qt5/plugins/platforms/libqxcb.so ] 2>/dev/null; then
  echo "NOTE: If smail fails with 'could not load Qt platform plugin xcb',"
  echo "      run: sudo apt install libqt5gui5 qt5-gtk-platformtheme"
fi
exit 0
EOF
chmod 0755 "${DEBIAN_DIR}/postinst"

cat > "${DEBIAN_DIR}/prerm" <<'EOF'
#!/bin/bash
set -e
exit 0
EOF
chmod 0755 "${DEBIAN_DIR}/prerm"

# ---------------------------------------------------------------------------
find "${PKG_ROOT}" -type d -exec chmod 0755 {} \;

DEB_FILE="${BUILD_DIR}/${APP_NAME}_${APP_VERSION}_${ARCH}.deb"
echo "==> Building .deb..."
dpkg-deb --build --root-owner-group "${PKG_ROOT}" "${DEB_FILE}"

DEB_SIZE=$(du -sh "${DEB_FILE}" | awk '{print $1}')
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  ✅  Build complete!                                 ║"
echo "╠══════════════════════════════════════════════════════╣"
printf "║  File: %-45s║\n" "$(basename "${DEB_FILE}") (${DEB_SIZE})"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  Install:  sudo apt install ./deb_build/$(basename "${DEB_FILE}") ║"
echo "║  Remove:   sudo apt remove smail                     ║"
echo "╚══════════════════════════════════════════════════════╝"
