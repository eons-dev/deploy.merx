import os
import logging
import shutil
from pathlib import Path
from emi import Merx, Epitome

class deploy(Merx):
    def __init__(this, name="Deploy"):
        super().__init__(name)

        this.transactionSucceeded = True
        this.rollbackSucceeded = False

    # Required Merx method. See that class for details.
    def Transaction(this):
        for tome in this.tomes:
            logging.info(f"Deploying {tome}...")
            epitome = this.GetTome(tome, "deployment")
            
            this.RunCommand(f"kubectl apply -f {str(epitome.path)}/*.yaml")
            
            this.catalog.add(epitome)

    # Required Merx method. See that class for details.
    def DidTransactionSucceed(this):
        return this.transactionSucceeded

    # Required Merx method. See that class for details.
    def Rollback(this):
        logging.error("Rollback not implemented")

    # Required Merx method. See that class for details.
    def DidRollbackSucceed(this):
        return this.rollbackSucceeded