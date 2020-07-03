# coding=utf-8

from odoo import models, fields, api
import json
import datetime


class WxConfirm(models.TransientModel):

    _name = 'wx.confirm'
    _description = u'确认'

    info = fields.Text("信息")
    model = fields.Char('模型')
    method = fields.Char('方法')

    @api.multi
    def execute(self):
        self.ensure_one()
        active_ids = self._context.get('record_ids')
        rs = self.env[self.model].browse(active_ids)
        ret = getattr(rs, self.method)()
        return ret

    @api.multi
    def execute_with_info(self):
        self.ensure_one()
        active_ids = self._context.get('record_ids')
        rs = self.env[self.model].browse(active_ids)
        ret = getattr(rs, self.method)(self.info)
        return ret

    def sale_order_sent(self, record_ids, ret_dict):
        sale_order = self.env['sale.order'].search([('date_order', '=', ret_dict.date_order)], limit=1)
        sale_order_id = sale_order.id
        sale_order_amount_total = sale_order.amount_total
        sale_order_user_id = sale_order.user_id.partner_id.name
        sale_order_create_uid = sale_order.create_uid.partner_id.name
        sale_order_date_order = ret_dict.date_order.strftime('%Y/%m/%d')
        corp_sales_adress = self.env["wx.corp.config"].search([]).mapped("corp_sales_adress")[0]
        if not corp_sales_adress:
            raise ValidationError('销售订单网址未填写或格式错误')
        info_str = "你有新的报价单\n" + \
                   "订单号：" + ret_dict.name + \
                   "\n订单日期：" + sale_order_date_order + \
                   "\n客户：" + ret_dict.partner_id.name + \
                   "\n销售员：" + sale_order_user_id+ \
                   "\n创建人：" + sale_order_create_uid + \
                   "\n订单金额：" + str(sale_order_amount_total) + \
                   "\n备注：" + ret_dict.note + \
                   "\n订单网址：" + corp_sales_adress.format(sale_order_id)
        #info = json.dumps('你有新的报价单', ensure_ascii=False) + json.dumps('订单号:', ensure_ascii=False) + json.dumps(ret_dict.name)
        #info = json.dumps(info_str, ensure_ascii=False)
        ret = getattr(record_ids, 'send_text')(info_str)
        return ret



class DateEnconding(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.date):
            return o.strftime('%Y/%m/%d')



