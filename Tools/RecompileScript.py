#Common Core RecompileScript.py
#Simple script used to compile Common Core.
#Distributed under the terms of the MIT License.
#For more information see https://github.com/KFPilot/CommonCore.
import argparse
from enum import Enum
import pathlib
import os
import subprocess
import shutil

class MissingPackagesError(Exception):
    pass

#Represents the kind of build we're trying to do.
class EBuildType(Enum):
    FULL = 0

ArgumentParser = argparse.ArgumentParser()
ArgumentParser.add_argument("-v", "--verboseUCC", action="store_true", help="Will log all of UCC make.")
ArgumentParser.add_argument("-s", "--stagefiles", action="store_true", help="Copies Common Core packages to staging directories.")
ArgumentParser.add_argument("--extrastage", help="Copies Common Core packages to a specified directory (such as a local test server). --stagefiles flag must be set.")

Arguments = ArgumentParser.parse_args()

#Type of build to do.
BuildType = EBuildType.FULL

#Files Common Core compiles.
CommonCoreFiles = ["CommonCore.u"]

#Files needed for Common Core deployments.
CommonCoreStagingFiles = [ "CommonCore.ucl" ]

StageFiles = Arguments.stagefiles
VerboseUCC = Arguments.verboseUCC

LocalPath = pathlib.Path().resolve()
SystemPath = LocalPath.joinpath("System")

GitHubStagingPath = LocalPath.joinpath("StagedCommonCore")
ExtraStagingPath = None

if Arguments.extrastage != None:
    ExtraStagingPath = pathlib.Path(Arguments.extrastage)

StepStrings = ["font "]
WarningStrings = ["warning", "unused local"]
ErrorStrings = ["error", "unresolved", "failed", "failure", "unknown property", "bad cast", "redundant data", "critical:", "not found"]

def PrintTask(String):
    print("\033[48;5;7m  \033[0m " + String)
def PrintStep(String):
    print("\033[48;5;7m \033[0m " + String)
def PrintWarning(String):
    print("\033[43m \033[0m \033[33m" + String + "\033[0m")
def PrintError(String):
    print("\033[41m \033[0m \033[31m" + String + "\033[0m")
def PrintSuccess(String):
    print("\033[48;2;0;200;0m \033[0m \033[38;2;0;200;0m" + String + "\033[0m")

def DeleteCommonCorePackages():
    for FileName in CommonCoreFiles:
        try:
            os.remove(SystemPath.joinpath(FileName))
        except FileNotFoundError as Error:
            print(f"{str(Error).split('\'')[0]} {FileName}")
        except Exception as Error:
            ErrorMessageSplit = str(Error).split('\'')[0]
            ErrorMessageSplit = ErrorMessageSplit.split(']')
            if len(ErrorMessageSplit) == 1:
                print(f"\033[33m {ErrorMessageSplit[0]} {FileName} \033[0m")
            else:
                print(f"\033[33m {ErrorMessageSplit[1]} {FileName} \033[0m")

def ProcessUCCMake(Process):
    HasReachedEnd = False
    FoundAnyErrors = False
    PreviousLine = ""
    while True:
        Line = Process.stdout.readline()

        if not Line:
            if not FoundAnyErrors:
                PrintSuccess("Compile completed without any errors.")
            break

        Line = Line.rstrip()

        if Line.startswith("Success - 0 error(s), 0 warning(s)"):
            HasReachedEnd = True

        if HasReachedEnd:
            if Line.startswith("Compile aborted") or Line.startswith("Failure -"):
                PrintError(Line)
                FoundAnyErrors = True
        elif Line.startswith("Analyzing..."):
            ModuleName = PreviousLine.replace("-", "").split(' ')[0]
            PrintStep(f"Compiling {ModuleName}...")
        elif any (FlagString in Line.lower() for FlagString in ErrorStrings):
            PrintError("  " + Line)
            FoundAnyErrors = True
        elif any (FlagString in Line.lower() for FlagString in WarningStrings):
            PrintWarning("  " + Line)
            FoundAnyErrors = True
        elif any (FlagString in Line.lower() for FlagString in StepStrings):
            PrintStep("  " + Line)

        PreviousLine = Line

        if not (Process.poll() is None):
            break

def RunUCCMake():
    UCCMakePath = LocalPath.joinpath(SystemPath, "UCC.exe")
    PrintTask("Running UCC make command...")
    try:
        if not VerboseUCC:
            UCCMakeProcess = subprocess.Popen([UCCMakePath, "make"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
            ProcessUCCMake(UCCMakeProcess)
        else:
            UCCMakeResult = subprocess.run([UCCMakePath, "make"], text=True, check=True)
    except subprocess.CalledProcessError as Error:
        print(f"Failed to run UCC make. Received return code {Error.returncode}.")
    print("... UCC make finished.")

def CheckIfAllFilesArePresent():
    MissingFiles = []
    for FileName in CommonCoreFiles:
        FilePath = SystemPath.joinpath(FileName)
        if not FilePath.is_file():
            MissingFiles.append(FileName)
    if len(MissingFiles) != 0:
        raise MissingPackagesError("Missing files: " + " ".join(MissingFiles))

def CopyCommonCoreFilesToTarget(Destination):
    PrintStep(f"Copying files to {Destination}...")
    for FileName in CommonCoreFiles:
        FilePath = SystemPath.joinpath(FileName)
        shutil.copy2(FilePath, Destination)
    for StagingFileName in CommonCoreStagingFiles:
        FilePath = SystemPath.joinpath(StagingFileName)
        shutil.copy2(FilePath, Destination)

def CopyCommonCoreFilesToDeployments():
    try:
        CopyCommonCoreFilesToTarget(GitHubStagingPath)
        if ExtraStagingPath != None:
            CopyCommonCoreFilesToTarget(ExtraStagingPath)
        PrintSuccess(f"Successfully copied files.")
    except Exception as Error:
        PrintError(f"{Error}")

def PerformCompile():
    DeleteCommonCorePackages()
    RunUCCMake()

    PrintTask("Checking for expected files...")
    FoundAllFiles = True
    try:
        CheckIfAllFilesArePresent()
        PrintSuccess("All expected files found.")
    except MissingPackagesError as Error:
        PrintError(f"{Error}")
        FoundAllFiles = False
    print("... expected file check complete.")
    
    if StageFiles and FoundAllFiles:
        PrintTask("Staging files...")
        CopyCommonCoreFilesToDeployments()
        print("... staging files finished.")

PerformCompile()