

from odoo_manager.template import ModuleTemplate
from odoo_manager.manager import get_config

template = ModuleTemplate(get_config())
template.name = 'sprintit_test'
template.add('models', 'account.invoice')
template.add('models', 'account.move.line')
template.add('wizards', 'download.account.statements')
template.add('wizards', 'upload.payment.order')
template.add('views', 'account.invoice')
template.add('views', 'download.account.statements')
template.add('views', 'upload.payment.order')
template.add('depends', 'account')
template.add('depends', 'hr_expense')
print(str(template))
