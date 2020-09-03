
# Ensure that a coin is provided
if [ -z "${COIN}" ]
  then echo "Please provide a coin as argument" && return 1
fi

# Ensure that a path is provided when using option "file"
if [ -n "${2}" ] && [ "${2}" = "file" ]
  then
    if [ -z "${3}" ]
      then echo "Please provide a path to the local compiled libcore" && return 1
    fi
fi

N_PROC=$(grep -c ^processor /proc/cpuinfo 2>/dev/null || sysctl -n hw.ncpu || echo 1)
echo "Number of processing units: ${N_PROC}"

# nvm
case "$(uname -s)" in
   Darwin)
     . $(brew --prefix nvm)/nvm.sh 
     ;;

   Linux)
     . ${HOME}/.nvm/nvm.sh 
     ;;
esac

if [ -d "${WORKDIR}" ]; then rm -rf ${WORKDIR} ; fi
mkdir ${WORKDIR}
cd ${WORKDIR}

set_node() {
    nvm use ${1}
    if [[ $( node --version | grep "v${1}" ) != *"v${1}"* ]]; then
        echo "Node version expected to be ${1}" && return 1;
    fi
}

get_value_from_config_file() {
  SOURCE=$( python3 ${SCRIPT_DIR}/read_config_file.py ${COIN} ${PRODUCT} ${1} ${2} )
  exitcode=$?
  if [ ${exitcode} != 0 ]; then return ${exitcode}; fi
  if [ -z "${SOURCE}" ]; then SOURCE=""; fi
  echo ${SOURCE}
}

retrieve_sources() {
    repository_uri=$( get_value_from_config_file ${1} 'repository' )
    repository_branch=$( get_value_from_config_file ${1} 'branch' )
    repository_commit=$( get_value_from_config_file ${1} 'commit' )

    cd ${WORKDIR}
    dir=$( basename "${repository_uri}" ".${repository_uri##*.}" )
    echo -e "\nCLONING ${repository_uri}...\n"
    git clone ${repository_uri} -j${N_PROC}

    cd "${WORKDIR}/${dir}"

    if [ -n "${repository_commit}" ]; then
          echo -e "\nCHECKOUT COMMIT: ${repository_commit}\n"
          git reset --hard "${repository_commit}"   
    elif [ -n "${repository_branch}" ]; then
          echo -e "\nCHECKOUT BRANCH: ${repository_branch}\n"
          git checkout "${repository_branch}"
    fi
  
    SOURCE_DIR=$( echo "${dir}" )
}

last_commit_id() {
    echo $( git log --format="%H" -n 1 )
}

remove_sources() {
    cd ${WORKDIR}
    if [ -d "${SOURCE_DIR}" ]; 
        then rm -rf ${SOURCE_DIR} ; 
    fi
}

pause() {
  read -p "Press enter to continue"
}

# Export variables from .env file
set -o allexport
source "${SCRIPT_DIR}/.env"
set +o allexport

# Remove existing db
rm -rf "${SCRIPT_DIR}/dbdata" || true