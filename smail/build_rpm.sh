#!/usr/bin/env bash
# =============================================================================
# build_rpm.sh — Package 'smail' as a .rpm (Poetry project)
#
# Usage:
#   ./build_rpm.sh
#
# Requirements (install on build machine):
#   Fedora/RHEL:  sudo dnf install rpm-build python3.14 python3.14-venv
#   openSUSE:     sudo zypper install rpm-build python312 python312-venv
#   poetry self add poetry-plugin-export
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
APP_NAME="smail"
APP_VERSION="0.1.8"
APP_RELEASE="1"                      # increment when repackaging same version
APP_DESCRIPTION="smail email client"
APP_MAINTAINER="Chladek Jan <253185@vutbr.cz>"
APP_LICENSE="MIT"
BIN_NAME="smail"
INSTALL_PREFIX="/opt/${APP_NAME}"
ARCH="x86_64"

# RPM dependency names (different from Debian!)
# PyQt5 pip wheel bundles Qt5 — only need xcb/gl/dbus runtime libs
RPM_REQUIRES="\
python3.14 \
libGL \
libEGL \
dbus-libs \
libxcb \
xcb-util-wm \
xcb-util-image \
xcb-util-keysyms \
xcb-util-renderutil \
libxkbcommon-x11 \
libXrandr"

SCONF_DIR="$(realpath ../sconf)"
# ---------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${SCRIPT_DIR}/rpm_build"

# rpmbuild expects a specific directory tree
RPM_ROOT="${BUILD_DIR}/rpmbuild"
RPM_SOURCES="${RPM_ROOT}/SOURCES"
RPM_SPECS="${RPM_ROOT}/SPECS"
RPM_BUILD="${RPM_ROOT}/BUILD"
RPM_RPMS="${RPM_ROOT}/RPMS"
RPM_SRPMS="${RPM_ROOT}/SRPMS"

# Staging dir — mirrors what will be installed on target
STAGE_DIR="${BUILD_DIR}/stage"
VENV_DIR="${STAGE_DIR}${INSTALL_PREFIX}"

# ---------------------------------------------------------------------------
# Sanity checks
# ---------------------------------------------------------------------------
echo "==> Checking prerequisites..."
[ -d "${SCONF_DIR}" ] || { echo "ERROR: sconf not found at ${SCONF_DIR}"; exit 1; }
for cmd in poetry python3.14 rpmbuild; do
  command -v "$cmd" &>/dev/null || { echo "ERROR: '$cmd' not found."; exit 1; }
done

# ---------------------------------------------------------------------------
# Clean
# ---------------------------------------------------------------------------
echo "==> Cleaning previous build..."
rm -rf "${BUILD_DIR}"
mkdir -p "${RPM_SOURCES}" "${RPM_SPECS}" "${RPM_BUILD}" "${RPM_RPMS}" "${RPM_SRPMS}"
mkdir -p "${VENV_DIR}" "${STAGE_DIR}/usr/local/bin"

# ---------------------------------------------------------------------------
# 1. Build sconf wheel
# ---------------------------------------------------------------------------
echo "==> Building sconf wheel..."
SCONF_DIST="${BUILD_DIR}/sconf_dist"
mkdir -p "${SCONF_DIST}"
(cd "${SCONF_DIR}" && POETRY_VIRTUALENVS_CREATE=false poetry build --format wheel --output "${SCONF_DIST}" -q)
SCONF_WHEEL=$(ls "${SCONF_DIST}"/*.whl | sort -V | tail -n1)
echo "    sconf: $(basename "${SCONF_WHEEL}")"

# ---------------------------------------------------------------------------
# 2. Export requirements
# ---------------------------------------------------------------------------
echo "==> Exporting requirements (excluding sconf)..."
POETRY_VIRTUALENVS_CREATE=false poetry export \
  --format requirements.txt \
  --output "${BUILD_DIR}/requirements.txt" \
  --without-hashes
sed -i '/sconf/Id' "${BUILD_DIR}/requirements.txt"

# ---------------------------------------------------------------------------
# 3. Build smail wheel
# ---------------------------------------------------------------------------
echo "==> Building smail wheel..."
POETRY_VIRTUALENVS_CREATE=false poetry build --format wheel -q
SMAIL_WHEEL=$(ls "${SCRIPT_DIR}/dist/smail-"*.whl | sort -V | tail -n1)
echo "    smail: $(basename "${SMAIL_WHEEL}")"

# ---------------------------------------------------------------------------
# 4. Create virtualenv and install everything
# ---------------------------------------------------------------------------
echo "==> Creating python3.14 virtualenv..."
python3.14 -m venv "${VENV_DIR}"
PIP="${VENV_DIR}/bin/pip"

echo "==> Upgrading pip..."
"${PIP}" install --quiet --upgrade pip

echo "==> Purging pip cache..."
"${PIP}" cache purge || true

echo "==> Installing requirements..."
"${PIP}" install --quiet --require-virtualenv -r "${BUILD_DIR}/requirements.txt"
"${PIP}" install --quiet --require-virtualenv "${SCONF_WHEEL}"
"${PIP}" install --quiet --require-virtualenv "${SMAIL_WHEEL}"

# ---------------------------------------------------------------------------
# 5. Patch venv paths for target machine
# ---------------------------------------------------------------------------
echo "==> Patching venv shebangs for ${INSTALL_PREFIX}..."
find "${VENV_DIR}/bin" -type f | while read -r f; do
  if file "$f" 2>/dev/null | grep -q "text"; then
    sed -i "s|${VENV_DIR}|${INSTALL_PREFIX}|g" "$f"
  fi
done
sed -i "s|${VENV_DIR}|${INSTALL_PREFIX}|g" "${VENV_DIR}/pyvenv.cfg"

echo "==> Recreating python symlinks..."
(
  cd "${VENV_DIR}/bin"
  rm -f python python3 python3.14
  ln -s /usr/bin/python3.14 python3.14
  ln -s python3.14 python3
  ln -s python3.14 python
)

# ---------------------------------------------------------------------------
# 6. Launcher script
# ---------------------------------------------------------------------------
echo "==> Writing launcher..."
LAUNCHER="${STAGE_DIR}/usr/local/bin/${BIN_NAME}"
mkdir -p "$(dirname "${LAUNCHER}")"
cat > "${LAUNCHER}" <<EOF
#!/bin/bash
exec "${INSTALL_PREFIX}/bin/python3.14" -m smail "\$@"
EOF
chmod 0755 "${LAUNCHER}"
[ -f "${LAUNCHER}" ] || { echo "ERROR: launcher not written"; exit 1; }

# ---------------------------------------------------------------------------
# 7. Create a tarball of the staged files (rpmbuild SOURCE)
# ---------------------------------------------------------------------------
echo "==> Creating source tarball..."
TARBALL_NAME="${APP_NAME}-${APP_VERSION}"
(cd "${STAGE_DIR}" && tar czf "${RPM_SOURCES}/${TARBALL_NAME}.tar.gz" .)
echo "    tarball: ${TARBALL_NAME}.tar.gz ($(du -sh "${RPM_SOURCES}/${TARBALL_NAME}.tar.gz" | awk '{print $1}'))"

# ---------------------------------------------------------------------------
# 8. Write the RPM spec file
# ---------------------------------------------------------------------------
echo "==> Writing spec file..."

# Build Requires line
REQUIRES_LINE=$(echo "${RPM_REQUIRES}" | tr '\n' ' ' | sed 's/  */ /g; s/^ //; s/ $//' | sed 's/ /, /g')

cat > "${RPM_SPECS}/${APP_NAME}.spec" <<SPECEOF
Name:           ${APP_NAME}
Version:        ${APP_VERSION}
Release:        ${APP_RELEASE}%{?dist}
Summary:        ${APP_DESCRIPTION}
License:        ${APP_LICENSE}
Packager:       ${APP_MAINTAINER}

Requires:       ${REQUIRES_LINE}

# Pre-built tarball — no compilation needed
%define         _build_id_links none
AutoReqProv:    no

Source0:        %{name}-%{version}.tar.gz

%description
${APP_DESCRIPTION}

%prep
# Nothing to prep — we ship a pre-built venv

%build
# Nothing to build

%install
# Unpack staged tree into RPM buildroot
mkdir -p %{buildroot}
tar xzf %{_sourcedir}/%{name}-%{version}.tar.gz -C %{buildroot}

%post
echo "smail installed. Run with: smail"

%preun
# Nothing needed on uninstall — RPM handles file removal

%files
%defattr(-,root,root,-)
${INSTALL_PREFIX}
/usr/local/bin/${BIN_NAME}

%changelog
* $(date "+%a %b %d %Y") ${APP_MAINTAINER} - ${APP_VERSION}-${APP_RELEASE}
- Initial RPM package
SPECEOF

# ---------------------------------------------------------------------------
# 9. Build the RPM
# ---------------------------------------------------------------------------
echo "==> Running rpmbuild..."
QA_RPATHS=0x003f \
rpmbuild \
  --define "_topdir ${RPM_ROOT}" \
  --define "_rpmdir ${RPM_RPMS}" \
  --define "__brp_check_rpaths %{nil}" \
  --define "__brp_mangle_shebangs %{nil}" \
  --target "${ARCH}" \
  -bb "${RPM_SPECS}/${APP_NAME}.spec"

RPM_FILE=$(find "${RPM_RPMS}" -name "*.rpm" | head -1)
RPM_SIZE=$(du -sh "${RPM_FILE}" | awk '{print $1}')

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  ✅  Build complete!                                 ║"
echo "╠══════════════════════════════════════════════════════╣"
printf "║  File: %-45s║\n" "$(basename "${RPM_FILE}") (${RPM_SIZE})"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  Fedora/RHEL:   sudo dnf install ./$(basename "${RPM_FILE}") ║"
echo "║  openSUSE:      sudo zypper install ./$(basename "${RPM_FILE}") ║"
echo "║  Remove:        sudo dnf remove smail                ║"
echo "╚══════════════════════════════════════════════════════╝"
