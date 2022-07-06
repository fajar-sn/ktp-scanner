class KTPInformation(object):
    def __init__(self):
        self.province = ""
        self.regency = ""
        self.id = ""
        self.name = ""
        self.birth_place = ""
        self.birth_date = ""
        self.gender = ""
        self.blood_group = ""
        self.address = ""
        self.rtrw = ""
        self.village = ""
        self.district = ""
        self.relligion = ""
        self.marriage_status = ""
        self.job = ""
        self.citizenship = ""
        self.valid_until = "SEUMUR HIDUP"

    def to_string(self) -> str:
        return f"\nKTP Information\n\nprovince: {self.province}\nregency: {self.regency}\nid: {self.id}\nname: {self.name}\nbirth place: {self.birth_place}\nbirth date: {self.birth_date}\ngender: {self.gender}\nblood group: {self.blood_group}\naddress: {self.address}\nrtrw: {self.rtrw}\nvillage: {self.village}\ndistrict: {self.district}\nrelligion: {self.relligion}\nmarriage status: {self.marriage_status}\njob: {self.job}\ncitizenship: {self.citizenship}\nvalid until: {self.valid_until}\n"
