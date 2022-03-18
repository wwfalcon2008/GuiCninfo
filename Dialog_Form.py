from PyQt5 import QtWidgets

from dialog import Ui_Dialog


# class DialogForm(QtWidgets.QWidget, Ui_Dialog):
class DialogForm(Ui_Dialog):
    def __init__(self, category):
        super(DialogForm, self).__init__()
        self.setupUi(self)
        self.category = category
        self.checkBox_list = [
            self.checkBox_ndbg_szsh,
            self.checkBox_bndbg_szsh,
            self.checkBox_yjdbg_szsh,
            self.checkBox_sjdbg_szsh,
            self.checkBox_yjygjxz_szsh,
            self.checkBox_qyfpxzcs_szsh,
            self.checkBox_dshgg_szsh,
            self.checkBox_jshgg_szsh,
            self.checkBox_gddh_szsh,
            self.checkBox_rcjy_szsh,
            self.checkBox_gszl_szsh,
            self.checkBox_zj_szsh,
            self.checkBox_sf_szsh,
            self.checkBox_zf_szsh,
            self.checkBox_gqjl_szsh,
            self.checkBox_pg_szsh,
            self.checkBox_jj_szsh,
            self.checkBox_gszq_szsh,
            self.checkBox_kzzq_szsh,
            self.checkBox_qtrz_szsh,
            self.checkBox_gqbd_szsh,
            self.checkBox_bcgz_szsh,
            self.checkBox_cqdq_szsh,
            self.checkBox_fxts_szsh,
            self.checkBox_tbclts_szsh,
            self.checkBox_tszlq_szsh
        ]
        self.checkBox_value = [
            'category_ndbg_szsh',
            'category_bndbg_szsh',
            'category_yjdbg_szsh',
            'category_sjdbg_szsh',
            'category_yjygjxz_szsh',
            'category_qyfpxzcs_szsh',
            'category_dshgg_szsh',
            'category_jshgg_szsh',
            'category_gddh_szsh',
            'category_rcjy_szsh',
            'category_gszl_szsh',
            'category_zj_szsh',
            'category_sf_szsh',
            'category_zf_szsh',
            'category_gqjl_szsh',
            'category_pg_szsh',
            'category_jj_szsh',
            'category_gszq_szsh',
            'category_kzzq_szsh',
            'category_qtrz_szsh',
            'category_gqbd_szsh',
            'category_bcgz_szsh',
            'category_cqdq_szsh',
            'category_fxts_szsh',
            'category_tbclts_szsh',
            'category_tszlq_szsh'
        ]
        # for cb in self.checkBox_list:
        #     cb.setCheckState(False)

    def dialog_all(self, event):
        for cb in self.checkBox_list:
            cb.setCheckState(True)

    def dialog_inverse(self, event):
        for cb in self.checkBox_list:
            cb.setCheckState(not cb.checkState())

    def dialog_ok(self, event):
        i = 0
        self._selected = []
        for cb in self.checkBox_list:
            if cb.checkState():
                self.category = self.category + self.checkBox_value[i] + ','
                self._selected.append(1)
            else:
                self._selected.append(0)
            i += 1
        if self.category == '':
            pass
        elif self.category[-1] == ',':
            self.category = self.category[:-1]
        print(self.category)
        self._output = self.category
        super(DialogForm, self).accept()

    def dialog_cancel(self, event):
        for cb in self.checkBox_list:
            cb.setCheckState(False)
            self.category = ''
        self.close()

    def get_output(self):
        return self._output

    def get_selected(self):
        return self._selected
