
ARG BUILD_TYPE=Debug
ARG LIB_CORE_SRC_DIR=/libcore/source
ARG LIB_CORE_BUILD_DIR=/libcore/build
ARG LIB_CORE_JAR_BUILD_DIR=/build-jar
ARG LIBCORE_AWS_BASE_URL=https://s3-eu-west-1.amazonaws.com/ledger-lib-ledger-core

# Compile
# (generates libledger-core.so)

FROM debian:stretch AS builder

ARG CMAKE_VERSION=3.15.2

ARG BUILD_TYPE
ARG DL_LIBCORE
ARG LIB_CORE_SRC_DIR
ARG LIB_CORE_BUILD_DIR
ARG LIBCORE_AWS_BASE_URL
ARG LIBCORE_VERSION

RUN apt-get update -qqy \
    && apt-get install -qqy \
        build-essential=12.3 \
        apt-transport-https=1.4.10 \
        curl \
        git=1:2.11.0-3+deb9u7 \
        ssh=1:7.4p1-10+deb9u7 \
        libssl-dev=1.1.0l-1~deb9u1 \
        libx11-xcb-dev=2:1.6.4-3+deb9u1 \
        qt5-default=5.7.1+dfsg-3+deb9u2 \
        libqt5websockets5=5.7.1~20161021-4 \
        libqt5websockets5-dev=5.7.1~20161021-4 \
        postgresql-9.6=9.6.17-0+deb9u1 \
        libpq-dev=9.6.17-0+deb9u1 \
        postgresql-server-dev-all=181+deb9u3 \
        sqlite3=3.16.2-5+deb9u1 \
        libsqlite3-dev=3.16.2-5+deb9u1 \
        # JDK is required as JNI is enabled:
        openjdk-8-jdk=8u252-b09-1~deb9u1 \
    && rm -rf /var/lib/apt/lists/*

RUN if [ "${DL_LIBCORE}" = "ON" ]; then exit 0; fi && \
    curl -LJO https://github.com/Kitware/CMake/releases/download/v${CMAKE_VERSION}/cmake-${CMAKE_VERSION}.tar.gz \
    && tar -zxf cmake-${CMAKE_VERSION}.tar.gz \
    && cd cmake-${CMAKE_VERSION} \
    && ./bootstrap \
    && make -j$(nproc) \
    && make install

COPY . ${LIB_CORE_SRC_DIR}

# Init submodules
RUN cd ${LIB_CORE_SRC_DIR} \
    # Use https for git to avoid permissions issues
    && git config --global url."https://github.com/".insteadOf git@github.com: \
    && git config --global url."https://".insteadOf git:// \
    && git submodule update --init --recursive --jobs=$(nproc) \
    && ( ( cd core/lib/leveldb && git checkout bitcoin-fork ) || exit 0 )

WORKDIR ${LIB_CORE_BUILD_DIR}

# Option 1: Compile
RUN if [ "$DL_LIBCORE" = "ON" ]; then exit 0; fi && \
    cmake_params="\
        # Common flags:
        -DCMAKE_BUILD_TYPE=${BUILD_TYPE} \
        -DTARGET_JNI=ON \
        -DSYS_OPENSSL=ON \
        -DOPENSSL_SSL_LIBRARIES=/usr/lib/x86_64-linux-gnu \
        -DOPENSSL_INCLUDE_DIR=/usr/include/openssl \
        -DCMAKE_INSTALL_PREFIX=/usr/share/qt5 \
        -DPG_SUPPORT=ON \
        -DPostgreSQL_INCLUDE_DIR=/usr/include/postgresql" \
            # Case 1: Release flag
            && if [ "${BUILD_TYPE}" = "Release" ] ; \ 
                then cmake_params="${cmake_params} -DBUILD_TESTS=OFF" \
            # Case 2: Debug flags
            ; elif [ "${BUILD_TYPE}" = "Debug" ] ; \
                then cmake_params="${cmake_params} -DBUILD_TESTS=ON" \              
            # Case 3: Unknown build type
            ; else echo "Error: unknown build type '${BUILD_TYPE}' \
                        (expected: 'Release' or 'Debug' (case sensitive))" \
                   && exit 1 \
            ; fi \
            && echo "cmake parameters (${BUILD_TYPE}): ${cmake_params}" \
        && cmake $cmake_params ${LIB_CORE_SRC_DIR} \
        # Avoid "clock skew detected" warning:
        && touch * \
        && make -j$(nproc) \
        && mv core/src/libledger-core.so libledger-core.so \
    ; fi

# Option 2: Download
RUN if [ "${DL_LIBCORE}" = "ON" ]; then \
        curl -k "${LIBCORE_AWS_BASE_URL}/${LIBCORE_VERSION}/linux/jni/libledger-core_jni.so" \
             --max-time 600 \
             --output libledger-core.so \
    ; fi

# Safeguard to ensure that libledger-core.so exists at this stage
RUN stat ${LIB_CORE_BUILD_DIR}/libledger-core.so


# Encapsulate compiled library in jar file
# (generates ledger-lib-core.jar)

FROM debian:stretch AS jar_generator

ARG LIB_CORE_SRC_DIR
ARG LIB_CORE_BUILD_DIR
ARG LIB_CORE_JAR_BUILD_DIR

ARG JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
ARG SBT_DEB=sbt-1.3.10.deb

RUN mkdir -p ${LIB_CORE_BUILD_DIR} ${LIB_CORE_JAR_BUILD_DIR}

RUN apt-get update -qqy \
    && apt-get install -qqy \
        apt-transport-https=1.4.10 \
        curl \
        openjdk-8-jdk=8u252-b09-1~deb9u1 \
    && rm -rf /var/lib/apt/lists/* 

RUN curl -L -o ${SBT_DEB} https://dl.bintray.com/sbt/debian/${SBT_DEB} \
    && dpkg -i ${SBT_DEB} \
    && rm ${SBT_DEB}

# Generate interfaces
WORKDIR ${LIB_CORE_SRC_DIR}

COPY --from=builder ${LIB_CORE_SRC_DIR} .

RUN chmod +x tools/generate_interfaces.sh \
    && ./tools/generate_interfaces.sh

# Package
WORKDIR ${LIB_CORE_JAR_BUILD_DIR}

RUN cp -v ${LIB_CORE_SRC_DIR}/api/core/java/* . \
    && cp -v ${LIB_CORE_SRC_DIR}/api/core/scala/* .

COPY --from=builder ${LIB_CORE_BUILD_DIR}/libledger-core.so \
                    src/main/resources/resources/djinni_native_libs/libledger-core.so

RUN sbt package

# Move the jar file to build directory and rename it
RUN find . -name \*.jar -exec mv {} ${LIB_CORE_BUILD_DIR}/ledger-lib-core.jar \;


# Make libledger-core.so and ledger-lib-core.jar available 
# to host or to another Docker image

FROM debian:stretch

ENTRYPOINT [ "cp" , "-rf" , ".", "/build" ]

ARG LIB_CORE_BUILD_DIR

WORKDIR ${LIB_CORE_BUILD_DIR}

COPY --from=builder ${LIB_CORE_BUILD_DIR}/libledger-core.so .
COPY --from=jar_generator ${LIB_CORE_BUILD_DIR}/ledger-lib-core.jar .

RUN mkdir /build