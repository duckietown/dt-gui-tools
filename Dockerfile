# parameters
ARG PROJECT_NAME
ARG PROJECT_DESCRIPTION
ARG PROJECT_MAINTAINER
# pick an icon from: https://fontawesome.com/v4.7.0/icons/
ARG PROJECT_ICON="cube"
ARG PROJECT_FORMAT_VERSION

# ==================================================>
# ==> Do not change the code below this line
ARG ARCH
ARG DISTRO
ARG DOCKER_REGISTRY
ARG BASE_REPOSITORY
ARG BASE_ORGANIZATION=duckietown
ARG BASE_TAG=${DISTRO}-${ARCH}
ARG LAUNCHER=default

# define base image
FROM ${DOCKER_REGISTRY}/${BASE_ORGANIZATION}/${BASE_REPOSITORY}:${BASE_TAG} as base

# novnc and websockify versions to use
ARG NOVNC_VERSION="9fe2fd0"
ARG WEBSOCKIFY_VERSION="3646575"
# recall all arguments
ARG ARCH
ARG DISTRO
ARG DOCKER_REGISTRY
ARG PROJECT_NAME
ARG PROJECT_DESCRIPTION
ARG PROJECT_MAINTAINER
ARG PROJECT_ICON
ARG PROJECT_FORMAT_VERSION
ARG BASE_TAG
ARG BASE_REPOSITORY
ARG BASE_ORGANIZATION
ARG LAUNCHER
# - buildkit
ARG TARGETPLATFORM
ARG TARGETOS
ARG TARGETARCH
ARG TARGETVARIANT

# check build arguments
RUN dt-args-check \
    "PROJECT_NAME" "${PROJECT_NAME}" \
    "PROJECT_DESCRIPTION" "${PROJECT_DESCRIPTION}" \
    "PROJECT_MAINTAINER" "${PROJECT_MAINTAINER}" \
    "PROJECT_ICON" "${PROJECT_ICON}" \
    "PROJECT_FORMAT_VERSION" "${PROJECT_FORMAT_VERSION}" \
    "ARCH" "${ARCH}" \
    "DISTRO" "${DISTRO}" \
    "DOCKER_REGISTRY" "${DOCKER_REGISTRY}" \
    "BASE_REPOSITORY" "${BASE_REPOSITORY}" \
    && dt-check-project-format "${PROJECT_FORMAT_VERSION}"

# define/create repository path
ARG PROJECT_PATH="${SOURCE_DIR}/${PROJECT_NAME}"
ARG PROJECT_LAUNCHERS_PATH="${LAUNCHERS_DIR}/${PROJECT_NAME}"
RUN mkdir -p "${PROJECT_PATH}" "${PROJECT_LAUNCHERS_PATH}"
WORKDIR "${PROJECT_PATH}"

# keep some arguments as environment variables
ENV DT_PROJECT_NAME="${PROJECT_NAME}" \
    DT_PROJECT_DESCRIPTION="${PROJECT_DESCRIPTION}" \
    DT_PROJECT_MAINTAINER="${PROJECT_MAINTAINER}" \
    DT_PROJECT_ICON="${PROJECT_ICON}" \
    DT_PROJECT_PATH="${PROJECT_PATH}" \
    DT_PROJECT_LAUNCHERS_PATH="${PROJECT_LAUNCHERS_PATH}" \
    DT_LAUNCHER="${LAUNCHER}"

# install apt dependencies
COPY ./dependencies-apt.txt "${PROJECT_PATH}/"
RUN dt-apt-install ${PROJECT_PATH}/dependencies-apt.txt

# install python3 dependencies
ARG PIP_INDEX_URL="https://pypi.org/simple"
ENV PIP_INDEX_URL=${PIP_INDEX_URL}
COPY ./dependencies-py3.* "${PROJECT_PATH}/"
RUN dt-pip3-install "${PROJECT_PATH}/dependencies-py3.*"

# copy the source code
COPY ./packages "${PROJECT_PATH}/packages"

# build packages
RUN . /opt/ros/${ROS_DISTRO}/setup.sh && \
  catkin build \
    --workspace ${CATKIN_WS_DIR}/

# install launcher scripts
COPY ./launchers/. "${PROJECT_LAUNCHERS_PATH}/"
RUN dt-install-launchers "${PROJECT_LAUNCHERS_PATH}"

# install scripts
COPY ./assets/entrypoint.d "${PROJECT_PATH}/assets/entrypoint.d"
COPY ./assets/environment.d "${PROJECT_PATH}/assets/environment.d"

# define default command
CMD ["bash", "-c", "dt-launcher-${DT_LAUNCHER}"]

# store module metadata
LABEL \
    # module info
    org.duckietown.label.project.name="${PROJECT_NAME}" \
    org.duckietown.label.project.description="${PROJECT_DESCRIPTION}" \
    org.duckietown.label.project.maintainer="${PROJECT_MAINTAINER}" \
    org.duckietown.label.project.icon="${PROJECT_ICON}" \
    org.duckietown.label.project.path="${PROJECT_PATH}" \
    org.duckietown.label.project.launchers.path="${PROJECT_LAUNCHERS_PATH}" \
    # format
    org.duckietown.label.format.version="${PROJECT_FORMAT_VERSION}" \
    # platform info
    org.duckietown.label.platform.os="${TARGETOS}" \
    org.duckietown.label.platform.architecture="${TARGETARCH}" \
    org.duckietown.label.platform.variant="${TARGETVARIANT}" \
    # code info
    org.duckietown.label.code.distro="${DISTRO}" \
    org.duckietown.label.code.launcher="${LAUNCHER}" \
    org.duckietown.label.code.python.registry="${PIP_INDEX_URL}" \
    # base info
    org.duckietown.label.base.organization="${BASE_ORGANIZATION}" \
    org.duckietown.label.base.repository="${BASE_REPOSITORY}" \
    org.duckietown.label.base.tag="${BASE_TAG}"
# <== Do not change the code above this line
# <==================================================

# configure ffmpeg
RUN mkdir /usr/local/ffmpeg \
    && ln -s /usr/bin/ffmpeg /usr/local/ffmpeg/ffmpeg

# install backend dependencies
COPY assets/vnc/install-backend-deps /tmp/
COPY assets/vnc/image/usr/local/lib/web/backend/requirements.txt /tmp/
RUN /tmp/install-backend-deps

# copy novnc stuff to the root of the container
COPY assets/vnc/image /


#### => Substep: Frontend builder
##
##  NOTE:   This substep always runs in an amd64 image regardless of the architecture of
##          the final image. As a result, this Dockerfile can be run only on amd64 machines
##          with QEMU enabled.
##
##
FROM ubuntu:focal as builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        git \
        ca-certificates \
        gnupg \
        patch

# nodejs
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash - \
    && apt-get install -y \
        nodejs

# yarn
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - \
    && echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list \
    && apt-get update \
    && apt-get install -y yarn

# fetch noVNC
ARG NOVNC_VERSION
RUN git clone https://github.com/novnc/noVNC /src/web/static/novnc \
    && git -C /src/web/static/novnc checkout ${NOVNC_VERSION}

# fetch websockify
ARG WEBSOCKIFY_VERSION
RUN git clone https://github.com/novnc/websockify /src/web/static/websockify \
    && git -C /src/web/static/websockify checkout ${WEBSOCKIFY_VERSION}

# build frontend
COPY assets/vnc/web /src/web
RUN cd /src/web \
    && yarn \
    && yarn build
RUN sed -i 's#app/locale/#novnc/app/locale/#' /src/web/dist/static/novnc/app/ui.js
##
##
#### <= Substep: Frontend builder


# jump back to the base image and copy frontend from builder stage
FROM base
COPY --from=builder /src/web/dist/ /usr/local/lib/web/frontend/

# make websockify executable
RUN ln -sf /usr/local/lib/web/frontend/static/websockify \
        /usr/local/lib/web/frontend/static/novnc/utils/websockify \
    && chmod +x /usr/local/lib/web/frontend/static/websockify/run

# configure novnc
ENV HTTP_PORT 8087

# get the image_pipeline (this is needed to avoid issues with python2 shebang)
RUN git clone https://github.com/ros-perception/image_pipeline.git

# uninstall opencv-python-headless as it obscures opencv-python
RUN pip3 uninstall --yes opencv-python-headless

# build packages
RUN . /opt/ros/${ROS_DISTRO}/setup.sh && \
  catkin build \
    --workspace ${CATKIN_WS_DIR}/
