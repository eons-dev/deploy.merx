import os
import logging
import shutil
import eons
from glob import glob
from pathlib import Path
from emi import Merx, Epitome

class deploy(Merx):
    def __init__(this, name="Deploy"):
        super().__init__(name)

        this.transactionSucceeded = True
        this.rollbackSucceeded = False

    @eons.recoverable
    def EvaluateLine(this, line):
        return eval(f"f\"{line[:-1]}\"") + "\n"

    # Required Merx method. See that class for details.
    def Transaction(this):
        for tome in this.tomes:
            logging.debug(f"Compiling {tome}...")
            epitome = this.GetTome(tome, tomeType="deployment")

            compiledOutputPath = this.executor.library.joinpath("deployment").joinpath(tome).joinpath(f"tome.compiled.yaml")
            epitome.installed_at = str(compiledOutputPath)
            compiledOutput = this.CreateFile(compiledOutputPath)

            for file in glob(f"{str(epitome.path)}/*.yaml"):
                logging.debug(f"Ingesting {file}")
                iFile = open(Path(file), 'r')
                for line in iFile:
                    try:
                        compiledOutput.write(this.EvaluateLine(line))
                    except Exception as e:
                        logging.error(str(e))
                iFile.close()
                compiledOutput.write('\n---\n')
            
            compiledOutput.close()

            logging.debug(f"Compiled as {compiledOutputPath}.")
    
            this.RunCommand(f"kubectl apply -f {epitome.installed_at}")
        
            this.catalog.add(epitome)

    # Required Merx method. See that class for details.
    def DidTransactionSucceed(this):
        return this.transactionSucceeded

    # Required Merx method. See that class for details.
    def Rollback(this):
        for tome in this.tomes:
            logging.info(f"Rolling back changes for {tome}...")
            epitome = this.GetTome(tome, tomeType="deployment")
            if (epitome is None):
                logging.error(f"UNABLE TO FIND EPITOME FOR {tome}! SYSTEM STATE UNKNOWN!!!")
                this.rollbackSucceeded = False
                #Uh oh... let's keep going and try to do what we can..
                continue

            this.RunCommand(f"kubectl delete -f {epitome.installed_at}")

        super().Rollback()


    # Required Merx method. See that class for details.
    def DidRollbackSucceed(this):
        return this.rollbackSucceeded