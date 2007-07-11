# this is for backward compatibilty, to be removed:
class Mmd5:
    def __init__(self):
        import md5
        self.md5 = md5.new("heja")
        self.value=int(self.md5.hexdigest(),16)

    def add(self, item):
        self.md5.update(str(item))
        self.value = int(self.md5.hexdigest(),16)
    addint = addstr = add
mhash = lambda : Mmd5()
