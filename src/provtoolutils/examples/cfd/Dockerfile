FROM ubuntu:22.04
#FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y python3 python3-pip unzip wget

RUN python3 -m pip install --upgrade pip setuptools wheel


################################################################################
# Prepare IPO folder structure
################################################################################

RUN mkdir /provtool_src && \
    mkdir /apps && \
    mkdir -p /examples/su2_cfd && \
    mkdir -p /examples/su2_cfd/flow/in && \
    mkdir -p /examples/su2_cfd/flow/out && \
    mkdir -p /examples/su2_cfd/adjoint/in && \
    mkdir -p /examples/su2_cfd/adjoint/in/config_modification && \
    mkdir -p /examples/su2_cfd/adjoint/in/restart && \
    mkdir -p /examples/su2_cfd/adjoint/out && \
    mkdir -p /examples/su2_cfd/visualization/in && \
    mkdir -p /examples/su2_cfd/visualization/out && \
    mkdir -p /tmp/su2_download && \
    mkdir -p /tmp/paraview_download


################################################################################
# Install provtoolutils
################################################################################

# COPY could be replaced with RUN --mount=type=bind,target=/provtool_src/utils,source=src/utils. Nevertheless, RUN --mount is not supported in older podman/docker versions.
COPY src/provtoolutils /provtool_src/provtoolutils
COPY src/provtoolutils_localcontainerreader /provtool_src/provtoolutils_localcontainerreader
COPY src/provtoolvis /provtool_src/provtoolvis
RUN pip install /provtool_src/provtoolutils && pip install /provtool_src/provtoolutils_localcontainerreader && pip install /provtool_src/provtoolvis

# Create agentinfo file with information about the current data creator. Can 
# also be supplied via cli without the need for a file.

ENV ACTIVITY_LOCATION="Docker image used for provtool example execution"
ARG GIVEN_NAME=""
ARG FAMILY_NAME="Dockerfile"

# Create a file containing the user information for further reuse.
RUN echo '{"agent": {"given_name": "'$GIVEN_NAME'", "family_name": "'$FAMILY_NAME'", "type": "person"}}' > /tmp/agentinfo.json


################################################################################
# Download SU2, Install SU2
################################################################################

WORKDIR /tmp/su2_download
# ENV could be ARG. Not used here because of cache problems in older podman versions
ENV SU2_DOWNLOAD_URL="https://github.com/su2code/SU2/releases/download/v7.3.1/SU2-v7.3.1-linux64.zip"
# Please see: https://github.com/su2code/SU2/blob/master/LICENSE.md for the respective SU2 license.
RUN wget $SU2_DOWNLOAD_URL && unzip SU2-v7.3.1-linux64.zip -d /apps/SU2-v7.3.1


################################################################################
# Download Paraview, Install Paraview
################################################################################

WORKDIR /tmp/paraview_download
RUN apt-get update && apt-get install -y libcurl4 libglvnd-dev
# There might be problems with the mesa drivers. In such a case try the paraview egl version
# ENV could be ARG. Not used here because of cache problems in older podman versions
ENV PARAVIEW_DOWNLOAD_URL="https://www.paraview.org/paraview-downloads/download.php?submit=Download&version=v5.9&type=binary&os=Linux&downloadFile=ParaView-5.9.1-osmesa-MPI-Linux-Python3.8-64bit.tar.gz"

# Please see: https://www.paraview.org/license/ for the applicable license. Please also note, that
# Paraview may contain additional libraries (for example scipy), which defines their own license.
RUN wget "$PARAVIEW_DOWNLOAD_URL" -O ParaView-5.9.1-osmesa-MPI-Linux-Python3.8-64bit.tar.gz && tar -xzf ParaView-5.9.1-osmesa-MPI-Linux-Python3.8-64bit.tar.gz -C /apps


################################################################################
# Generate provenance for tool
################################################################################

WORKDIR /tmp
RUN echo '{"activity": {"location": "'$ACTIVITY_LOCATION'", "label": "Download SU2 binary", "means": "Download of SU2 from '$SU2_DOWNLOAD_URL'"}}' | \
        python3  \
            -m provtoolutils.directorywrapper  \
            --configfile /dev/stdin  \
            --agentinfo /tmp/agentinfo.json  \
            --outputdir /tmp/su2_download  \
            --start $(date +%FT%T)"+00:00"  \
            --end $(date +%FT%T)"+00:00" && \
    echo '{"activity": {"location": "'$ACTIVITY_LOCATION'", "label": "Download Paraview binary", "means": "Download of Paraview from '$PARAVIEW_DOWNLOAD_URL'"}}' | \
        python3  \
            -m provtoolutils.directorywrapper  \
            --configfile /dev/stdin  \
            --agentinfo /tmp/agentinfo.json  \
            --outputdir /tmp/paraview_download  \
            --start $(date +%FT%T)"+00:00"  \
            --end $(date +%FT%T)"+00:00" && \
    find /tmp/ -iname directorywrapper.log | xargs -I{} rm {}


################################################################################
# Download tutorial files
################################################################################

# Please see: https://github.com/su2code/SU2/blob/master/LICENSE.md for the respective SU2 license.
RUN wget https://raw.githubusercontent.com/su2code/SU2/master/QuickStart/inv_NACA0012.cfg -O /examples/su2_cfd/flow/in/inv_NACA0012.cfg && \
    wget https://raw.githubusercontent.com/su2code/SU2/master/QuickStart/mesh_NACA0012_inv.su2 -O /examples/su2_cfd/flow/in/mesh_NACA0012_inv.su2 && \
    echo '{"activity": {"location": "'$ACTIVITY_LOCATION'", "label": "Download tutorial files", "means": "Download tutorial files from github"}}' | \
        python3  \
            -m provtoolutils.directorywrapper  \
            --configfile /dev/stdin  \
            --agentinfo /tmp/agentinfo.json  \
            --outputdir /examples/su2_cfd/flow/in  \
            --start $(date +%FT%T)"+00:00"  \
            --end $(date +%FT%T)"+00:00" && \
    find /examples -iname directorywrapper.log | xargs -I{} rm {}



################################################################################
# Simulate flow around geometry
################################################################################
WORKDIR /examples/su2_cfd/flow/in
RUN cp /tmp/su2_download/*.prov .
RUN touch timestamp && \
    /apps/SU2-v7.3.1/bin/SU2_CFD inv_NACA0012.cfg && find . -type f -newer timestamp -exec mv {} ../out \; && \
    rm timestamp && \
    echo '{"activity": {"location": "'$ACTIVITY_LOCATION'", "label": "Simulate flow", "means": "Performing the flow simulation of external, inviscid flow around a 2D geometry"}}' | \
        python3  \
            -m provtoolutils.directorywrapper  \
            --configfile /dev/stdin  \
            --agentinfo /tmp/agentinfo.json  \
            --inputdir /examples/su2_cfd/flow/in  \
            --outputdir /examples/su2_cfd/flow/out  \
            --start $(date +%FT%T)"+00:00"  \
            --end $(date +%FT%T)"+00:00" && \
    find /examples -iname directorywrapper.log | xargs -I{} rm {}


################################################################################
# Simulate sensitivities
################################################################################

WORKDIR /examples/su2_cfd/adjoint/in
RUN cp /tmp/su2_download/*.prov .
RUN python3 -m provtoolutils.search --entityname inv_NACA0012.cfg --searchdir /examples/su2_cfd/flow/in | \
        xargs -I{} cp {} /examples/su2_cfd/adjoint/in/config_modification && \
    cp /examples/su2_cfd/flow/in/inv_NACA0012.cfg /examples/su2_cfd/adjoint/in/config_modification && \
    python3 -m provtoolutils.search --entityname mesh_NACA0012_inv.su2 --searchdir /examples/su2_cfd/flow/in | \
        xargs -I{} cp {} /examples/su2_cfd/adjoint/in && \
    cp /examples/su2_cfd/flow/in/mesh_NACA0012_inv.su2 /examples/su2_cfd/adjoint/in && \
    sed -i -e 's/MATH_PROBLEM *= *DIRECT/MATH_PROBLEM=CONTINUOUS_ADJOINT/g' /examples/su2_cfd/adjoint/in/config_modification/inv_NACA0012.cfg && \
    mv /examples/su2_cfd/adjoint/in/config_modification/inv_NACA0012.cfg /examples/su2_cfd/adjoint/in/config_modification/inv_NACA0012_adj.cfg && \
    echo '{"activity": {"location": "'$ACTIVITY_LOCATION'", "label": "Configuration modification", "means": "Switch to adjoint method"}}' | \
        python3 \
            -m provtoolutils.directorywrapper \
            --configfile /dev/stdin \
            --agentinfo /tmp/agentinfo.json \
            --inputdir /examples/su2_cfd/adjoint/in/config_modification \
            --outputdir /examples/su2_cfd/adjoint/in/config_modification \
            --start $(date +%FT%T)"+00:00" \
            --end $(date +%FT%T)"+00:00" && \
    find /examples -iname directorywrapper.log | xargs -I{} rm {} && \
    python3 -m provtoolutils.search --entityname restart_flow.dat --searchdir /examples/su2_cfd/flow/out | \
        xargs -I{} cp {} /examples/su2_cfd/adjoint/in/restart && \
    cp /examples/su2_cfd/flow/out/restart_flow.dat /examples/su2_cfd/adjoint/in/restart/solution_flow.dat && \
    echo '{"activity": {"location": "'$ACTIVITY_LOCATION'", "label": "Renaming of solution file", "means": "Rename restart file to be used in adjoint method as solution file"}}' | \
        python3  \
            -m provtoolutils.directorywrapper  \
            --configfile /dev/stdin  \
            --agentinfo /tmp/agentinfo.json  \
            --inputdir /examples/su2_cfd/adjoint/in/restart  \
            --outputdir /examples/su2_cfd/adjoint/in/restart  \
            --start $(date +%FT%T)"+00:00"  \
            --end $(date +%FT%T)"+00:00" && \
    find /examples -iname directorywrapper.log | xargs -I{} rm {} && \
    mv /examples/su2_cfd/adjoint/in/config_modification/* /examples/su2_cfd/adjoint/in/ && \
    mv /examples/su2_cfd/adjoint/in/restart/* /examples/su2_cfd/adjoint/in/ && \
    rm -rf /examples/su2_cfd/adjoint/in/config_modification/ && \
    rm -rf /examples/su2_cfd/adjoint/in/restart
RUN touch timestamp && \
    /apps/SU2-v7.3.1/bin/SU2_CFD inv_NACA0012_adj.cfg && \
    find . -type f -newer timestamp -exec mv {} ../out \; && \
    rm timestamp && \
    echo '{"activity": {"location": "'$ACTIVITY_LOCATION'", "label": "Simulate sensitivities", "means": "Performing the flow simulation of external, inviscid flow around a 2D geometry"}}' | \
        python3  \
            -m provtoolutils.directorywrapper  \
            --configfile /dev/stdin  \
            --agentinfo /tmp/agentinfo.json  \
            --inputdir /examples/su2_cfd/adjoint/in  \
            --outputdir /examples/su2_cfd/adjoint/out  \
            --start $(date +%FT%T)"+00:00"  \
            --end $(date +%FT%T)"+00:00" && \
    find /examples -iname directorywrapper.log | xargs -I{} rm {}


################################################################################
# Simulate sensitivities
################################################################################

WORKDIR /examples/su2_cfd/visualization/in
RUN cp /tmp/paraview_download/*.prov . && \
    cp /provtool_src/provtoolutils/examples/cfd/*.prov . && \
    cp /provtool_src/provtoolutils/examples/cfd/surface_*.py . && \
    python3 -m provtoolutils.search --entityname surface_flow.vtu --searchdir /examples/su2_cfd/flow/out | \
        xargs -I{} cp {} . && \
    cp /examples/su2_cfd/flow/out/surface_flow.vtu . && \
    python3 -m provtoolutils.search --entityname surface_adjoint.vtu --searchdir /examples/su2_cfd/adjoint/out | \
        xargs -I{} cp {} . && \
    cp /examples/su2_cfd/adjoint/out/surface_adjoint.vtu . && \
    /apps/ParaView-5.9.1-osmesa-MPI-Linux-Python3.8-64bit/bin/pvbatch surface_flow.py && \
    /apps/ParaView-5.9.1-osmesa-MPI-Linux-Python3.8-64bit/bin/pvbatch surface_adjoint.py && \
    echo '{"activity": {"location": "'$ACTIVITY_LOCATION'", "label": "Visualize", "means": "Generaing visualizations for the simulation results"}}' | \
        python3  \
            -m provtoolutils.directorywrapper  \
            --configfile /dev/stdin  \
            --agentinfo /tmp/agentinfo.json  \
            --inputdir /examples/su2_cfd/visualization/in \
            --outputdir /examples/su2_cfd/visualization/out \
            --start $(date +%FT%T)"+00:00"  \
            --end $(date +%FT%T)"+00:00" && \
    find /examples -iname directorywrapper.log | xargs -I{} rm {}


################################################################################
# Generate quilt matrix
################################################################################

WORKDIR /examples/su2_cfd
RUN mkdir /tmp/quilt && \
    find /examples/su2_cfd/ -iname "*.prov" | xargs -I{} cp {} /tmp/quilt/ && \
    python3 -m provtoolvis.file2quilt /tmp/quilt $(python3 -m provtoolutils.search --searchdir /tmp/quilt --entityname surface_flow.png | sed 's/.prov//' | sed 's/.*\///') quilt.jpeg
