from getmodelspec.src.sony import GetSONY,  GetSONYjp

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

        dfModels = sony.getModels()
        return dfModels




