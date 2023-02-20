from dataclasses import dataclass
from datetime import date
from typing import Iterable, Optional
from services.data_access_objects import OrderDAO


@dataclass
class ReportRow:
    product_id: int
    product_name: str
    total_quantity: int


class MakeSalesReportService:
    """ Сервис создания отчета продаж по самым продаваемым товарам """

    @classmethod
    def _report_to_entity(cls, report: tuple) -> ReportRow:
        return ReportRow(
            product_id=report[0][0],
            product_name=report[0][1],
            total_quantity=report[1],
        )

    @classmethod
    def execute(cls, start: Optional[date], end: Optional[date]) -> Optional[Iterable[ReportRow]]:
        """ Возвращает отчет по продажам в интервале дат [start, end] """

        orders = OrderDAO.fetch_on_dates(start=start, end=end)
        if not orders:
            return None
        report = dict()
        for order in orders:
            for line in order.order_lines:
                if (line.product.id, line.product.name) in report:
                    report[(line.product.id, line.product.name)] += line.quantity
                else:
                    report[(line.product.id, line.product.name)] = line.quantity
        report = sorted(report.items(), key=lambda item: item[1], reverse=True)
        return map(cls._report_to_entity, report)
