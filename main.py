import requests
import base64
import re
import os
import subprocess

orgName = "ShaileshJadhav12"
projectName = "Demo"
targetOrgName="kabirkanjani"
targetProjectName="Testing"

# Get FileName from Response
def getFilename_fromCd(cd):
    if not cd:
        return None
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return None
    return fname[0]


# PAT and Authorization Headers
pat = 'ey5efzjybdpzexapsvuwy5kf5jwburdrrumfzs6o7jodilkpsvya'
authorization = str(base64.b64encode(bytes(':' + pat, 'ascii')), 'ascii')

headers = {
    'Accept': 'application/json',
    'Authorization': 'Basic ' + authorization
}


def getTargetHeaders():
    pat = 'w2awz3o5bjiiboat6tivem74dfqdwfhw2cpuhb3xtjuz5p2qraea'
    authorization = str(base64.b64encode(bytes(':' + pat, 'ascii')), 'ascii')

    headers = {
        'Accept': 'application/json',
        'Authorization': 'Basic ' + authorization
    }
    return headers


def createNupkgFile(Feed, package_name, version):
    response = requests.get(
        url=f"https://pkgs.dev.azure.com/{orgName}/{projectName}/_apis/packaging/feeds/{Feed}/nuget/packages/{package_name}/versions/{version}/content?api-version=7.0-preview.1",
        headers=headers)
    print(response.status_code)
    # Checking for Overwrites or other errors
    if response.status_code != 404:
        # Saving data to the file
        filename = getFilename_fromCd(response.headers.get('content-disposition'))
        package_filename = f'./projects/{package_name}r-{version}.nupkg'

        # Uploading the file to new Feed
        with open(package_filename, 'wb') as write_file:
            write_file.write(response.content)
            print(f"---------------------{package_name}r-{version}.nupkg file created---------------------")
        pushToFeed(Feed, package_filename)


def CreateFeed(name, scope):
    body = {"name": name}
    # if scope == "Project":
    response = requests.post(
        f"https://feeds.dev.azure.com/{targetOrgName}/{targetProjectName}/_apis/packaging/feeds?api-version=7.0",
        json=body, headers=getTargetHeaders())
    if response.status_code == 201:
        print(
            f"---------------------Feed with {name} created in {targetOrgName} inside {targetProjectName}---------------------")
        return True
    elif response.status_code == 409:
        print(
            f"---------------------Feed with {name} already exists in {targetOrgName} inside {targetProjectName}---------------------")
        return False
    else:
        print(response.status_code)
        return False
    # else:
    #     response = requests.post(f"https://feeds.dev.azure.com/{orgName}/_apis/packaging/feeds?api-version=7.0",
    #                              json=body, headers=headers)
    #     if response.status_code == 201:
    #         print(
    #             f"---------------------Feed with {name} created in {orgName} ---------------------")
    #         return True
    #     else:
    #         print(response)
    #         return False


def authenticateAz(Feed):
    command = f".\\nuget.exe sources add -name {Feed} -source  https://pkgs.dev.azure.com/{targetOrgName}/{targetProjectName}/_packaging/{Feed}/nuget/v3/index.json -username Kabir -password w2awz3o5bjiiboat6tivem74dfqdwfhw2cpuhb3xtjuz5p2qraea"
    print(command)
    subprocess.call(command, shell=True)

def pushToFeed(Feed, package_filename):
    CreateFeed(Feed, scope="Project")
    authenticateAz(Feed)
    command = f".\\nuget.exe push -Source https://pkgs.dev.azure.com/{targetOrgName}/{targetProjectName}/_packaging/{Feed}/nuget/v3/index.json -ApiKey az {package_filename} -SkipDuplicate"
    print(command)
    # os.system(f'cmd /k {command}')
    subprocess.call(command, shell=True)


def main():
    # Hitting URL to Fetch All Feed names
    response = requests.get(
        url=f"https://feeds.dev.azure.com/{orgName}/{projectName}/_apis/packaging/feeds?api-version=7.0",
        headers=headers)
    data = response.json()
    for name in data.get('value'):
        val = name.get('name')
        print(f"---------------------Feed {val} Fetched---------------------")
        # Fetching Feed name one by one and fetching packages names
        response = requests.get(
            url=f"https://feeds.dev.azure.com/{orgName}/{projectName}/_apis/packaging/Feeds/{val}/packages?api-version=7.1-preview.1",
            headers=headers)
        data1 = response.json()
        # Fetching Packages Names and versions to fetch the packages
        for name in data1.get('value'):
            package_name = name.get('normalizedName')
            version = name.get('versions')[0].get('normalizedVersion')
            # Downloading the packages
            print(f"---------------------Package {package_name}---------------------")
            createNupkgFile(val, package_name, version)

#
# def AddFeedtoOrg(Feed):
#     CreateFeed(Feed)
#     command = f".\\nuget.exe sources add -Name {Feed} -Source https://pkgs.dev.azure.com/{targetOrgName}/_packaging/OrgFeed/nuget/v3/index.json"
#     # os.system(f'cmd /k {command}')
#     subprocess.call(command, shell=True)

main()
