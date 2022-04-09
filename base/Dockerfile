# Compiling LibreOffice can take several hours. It can be done faster by
# using a machine with an SSD and multiple CPUs (e.g. an AWS C6 EC2 instance).
#
# A prebuilt headless LibreOffice that has been compiled for Amazon Linux 2
# (and is the output of this build) can be obtained from
# https://hub.docker.com/repository/docker/unofunction/libreoffice
FROM --platform=linux/amd64 amazonlinux:2 as build

ARG LIBREOFFICE_VERSION=7.3.2.2
ARG DOWNLOAD_PATH=https://github.com/LibreOffice/core/archive/libreoffice-${LIBREOFFICE_VERSION}.tar.gz

# Install build dependencies
RUN yum install -y yum-utils \
    && yum-config-manager --enable epel \
    && yum install -y \
    autoconf \
    ccache \
    expat-devel \
    fontconfig-devel \
    git \
    gmp-devel \
    google-crosextra-caladea-fonts \
    google-crosextra-carlito-fonts \
    icu \
    libcurl-devel \
    liberation-sans-fonts \
    liberation-serif-fonts \
    libffi-devel \
    libICE-devel \
    libicu-devel \
    libmpc-devel \
    libpng-devel \
    libSM-devel \
    libX11-devel \
    libXext-devel \
    libXrender-devel \
    libxslt-devel \
    mesa-libGL-devel \
    mesa-libGLU-devel \
    mpfr-devel \
    nasm \
    nspr-devel \
    nss-devel \
    openssl-devel \
    perl-Digest-MD5 \
    python3-devel \
    which
RUN yum groupinstall -y "Development Tools"

# The Amazon Linux 2 core repository is not kept up-to-date
# Some packages need to be installed from CentOS' repositories
RUN yum install -y \
    https://vault.centos.org/centos/8/AppStream/x86_64/os/Packages/liblangtag-0.6.2-8.el8.x86_64.rpm \
    https://vault.centos.org/centos/8/AppStream/x86_64/os/Packages/liblangtag-data-0.6.2-8.el8.noarch.rpm \
    https://vault.centos.org/centos/8/PowerTools/x86_64/os/Packages/gperf-3.1-5.el8.x86_64.rpm \ 
    https://vault.centos.org/centos/8/AppStream/x86_64/os/Packages/flex-2.6.1-9.el8.x86_64.rpm

# LibreOffice should not be installed as root
RUN groupadd -g 9999 libreoffice \ 
    && useradd -r -u 9999 -g libreoffice libreoffice
USER libreoffice

# Download LibreOffice source file
RUN cd /tmp \
    && curl -L ${DOWNLOAD_PATH} | tar -xz \
    && mv core-libreoffice-${LIBREOFFICE_VERSION} libreoffice

WORKDIR /tmp/libreoffice

# Prepare installation
ARG LC_CTYPE=en_US.UTF-8
ARG LC_ALL=en_US.UTF-8
RUN echo "lo_sources_ver=${LIBREOFFICE_VERSION}" >> sources.ver
RUN ./autogen.sh \
    --disable-avahi \
    --disable-cairo-canvas \
    --disable-coinmp \
    --disable-cups \
    --disable-cve-tests \
    --disable-dbus \
    --disable-dconf \
    --disable-dependency-tracking \
    --disable-evolution2 \
    --disable-dbgutil \
    --disable-extension-integration \
    --disable-extension-update \
    --disable-firebird-sdbc \
    --disable-gio \
    --disable-gstreamer-1-0 \
    --disable-gtk3 \
    --disable-introspection \
    --disable-largefile \
    --disable-lotuswordpro \
    --disable-lpsolve \
    --disable-odk \
    --disable-ooenv \
    --disable-pch \
    --disable-postgresql-sdbc \
    --disable-python \
    --disable-randr \
    --disable-report-builder \
    --disable-scripting-beanshell \
    --disable-scripting-javascript \
    --disable-sdremote \
    --disable-sdremote-bluetooth \
    --enable-mergelibs \
    --with-galleries="no" \
    --with-system-curl \
    --with-system-expat \
    --with-system-libxml \
    --with-system-nss \
    --with-system-openssl \
    --with-theme="no" \
    --without-export-validation \
    --without-fonts \
    --without-helppack-integration \
    --without-java \
    --without-junit \
    --without-krb5 \
    --without-myspell-dicts \
    --without-system-dicts

RUN make

# Strip symbols from object files
RUN strip ./instdir/**/* || true

# Not needed to run LibreOffice in --headless mode
RUN rm -rf /tmp/libreoffice/instdir/share/gallery \
    ./instdir/share/config/images_*.zip \
    ./instdir/readmes 



# Copy only the necessary files from the build image
FROM amazonlinux:2 as libreoffice

# LibreOffice
COPY --from=build /tmp/libreoffice/instdir /opt/libreoffice
COPY --from=build /usr/lib64 /usr/lib64

# Fonts
COPY --from=build /etc/fonts /etc/fonts
COPY --from=build /usr/include/X11/fonts /usr/include/X11/fonts
COPY --from=build /usr/share/fonts /usr/share/fonts
