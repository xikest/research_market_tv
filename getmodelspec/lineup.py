from getmodelspec.src.sony import GetSONY,  GetSONYjp
from getmodelspec.src.panasonic import GetPanajp
class LineUp:

    def __init__(self):

        pass
    def getSony(self, src="jp", fastMode: bool = True,  toExcel: bool = True) -> None:
        """
        src = "global" : global site
        src = "jp" : jp site
        """

        if src == "global":
            sony = GetSONY(fastMode=fastMode, toExcel=toExcel)
        elif "jp":
            sony = GetSONYjp(toExcel=toExcel)

        dictModels = sony.getModels()
        return dictModels

    def getPana(self, toExcel: bool = True) -> None:
        """

        """
        pana = GetPanajp(toExcel=toExcel)

        dictModels = pana.getModels()
        return dictModels




