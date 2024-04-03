from base64 import b64decode
from io import BytesIO
from logging import getLogger

from PIL import Image

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

logger = getLogger(__name__)

try:
    # we need this to be sure PIL has loaded PDF support
    from PIL import PdfImagePlugin  # noqa: F401
    logger.info("PIL imported")
except ImportError:
    logger.error("ImportError: The PdfImagePlugin could not be imported")

try:
    from PyPDF2 import PdfFileReader, PdfFileWriter  # pylint: disable=W0404
    from PyPDF2.utils import PdfReadError  # pylint: disable=W0404
    logger.info("PyPDF2 imported")
except ImportError:
    logger.error("Can not import PyPDF2")


class Report(models.Model):
    _inherit = "ir.actions.report"

    consider_watermark = fields.Boolean(
        default=False,
        help="Consider using the pdf watermark",
    )    


    def _render_qweb_pdf(self, res_ids=None, data=None):
        if not self.env.context.get("res_ids"):
            return super(Report, self.with_context(res_ids=res_ids))._render_qweb_pdf(
                res_ids=res_ids, data=data
            )
        return super(Report, self)._render_qweb_pdf(res_ids=res_ids, data=data)

    def pdf_has_usable_pages(self, numpages):
        if numpages < 1:
            logger.error("Your watermark pdf does not contain any pages")
            return False
        if numpages > 1:
            logger.debug(
                "Your watermark pdf contains more than one page, "
                "all but the first one will be ignored"
            )
        return True    

    @api.model
    def _run_wkhtmltopdf(
        self,
        bodies,
        header=None,
        footer=None,
        landscape=False,
        specific_paperformat_args=None,
        set_viewport_size=False,
    ):
        result = super(Report, self)._run_wkhtmltopdf(
            bodies,
            header=header,
            footer=footer,
            landscape=landscape,
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size,
        )

        docids = self.env.context.get("res_ids", False)


        if not self.consider_watermark:
            return result

        watermark = None
        publication_id = self.env.context.get("publication_id")
        if publication_id:
            publication = self.env['pricelist.publication'].browse(publication_id)
            if publication.pdf_background:
                watermark = b64decode(publication.pdf_background)

        if not watermark:
            return result

        pdf = PdfFileWriter()
        pdf_watermark = None
        try:
            pdf_watermark = PdfFileReader(BytesIO(watermark))
        except PdfReadError:
            # let's see if we can convert this with pillow
            try:
                Image.init()
                image = Image.open(BytesIO(watermark))
                pdf_buffer = BytesIO()
                if image.mode != "RGB":
                    image = image.convert("RGB")
                resolution = image.info.get("dpi", self.paperformat_id.dpi or 90)
                if isinstance(resolution, tuple):
                    resolution = resolution[0]
                image.save(pdf_buffer, "pdf", resolution=resolution)
                pdf_watermark = PdfFileReader(pdf_buffer)
            except Exception as e:
                logger.exception("Failed to load watermark", e)

        if not pdf_watermark:
            logger.error("No usable watermark found, got %s...", watermark[:100])
            return result

        if not self.pdf_has_usable_pages(pdf_watermark.numPages):
            return result

        page_number = 0

        for page in PdfFileReader(BytesIO(result)).pages:
            watermark_page = pdf.addBlankPage(
                page.mediaBox.getWidth(), page.mediaBox.getHeight()
            )
            if page_number == 0 :
                watermark_page.mergePage(pdf_watermark.getPage(0))
            watermark_page.mergePage(page)
            page_number += 1

        pdf_content = BytesIO()
        pdf.write(pdf_content)

        return pdf_content.getvalue()