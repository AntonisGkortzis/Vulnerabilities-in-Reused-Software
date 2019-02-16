#!/bin/bash

echo "ICSR '19 - Gkortzis et al. - Vendor tools"
echo "This script downloads the vendor tools necessary for the study."
echo "It will attempt to download the tools to folder './vendor'"
echo "It will attempt to download the following tools"
echo "- SpotBugs version 3.1.11"
echo "- SpotBugs plugin - FindSecBugs version 1.8.0"

download_vendor() {
    tool_dir="${1:?}"

    sb_version="3.1.11"
    fsb_version="1.8.0"

    download_spotbugs "$tool_dir" "$sb_version"
    download_findsecbugs "$tool_dir" "$sb_version" "$fsb_version"
}

download_spotbugs() {
    tool_dir="${1:?}"
    sb_version="${2:?}"
    sb_tgz="spotbugs-${sb_version}.tgz"
    sb_path="${tool_dir}/${sb_tgz}"
    sb_url="http://repo.maven.apache.org/maven2/com/github/spotbugs/spotbugs/${sb_version}/${sb_tgz}"
    
    [[ -d "$sb_path" ]] && rm -rf "$sb_path"
    wget -O "$sb_path" "$sb_url"
    tar -xvzf "$sb_path" -C "$tool_dir"
    rm "$sb_path"
}

download_findsecbugs() {
    tool_dir="${1:?}"
    sb_version="${2:?}"
    fsb_version="${3:?}"
    fsb_path="${tool_dir}/spotbugs-${sb_version}/plugin/findsecbugs-plugin-${fsb_version}.jar"
    fsb_url="https://search.maven.org/remotecontent?filepath=com/h3xstream/findsecbugs/findsecbugs-plugin/${fsb_version}/findsecbugs-plugin-${fsb_version}.jar"
    
    wget -O "$fsb_path" "$fsb_url"
}

download_vendor "./vendor" "3.1.11"
