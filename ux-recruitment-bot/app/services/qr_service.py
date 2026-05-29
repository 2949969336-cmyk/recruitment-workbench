from io import BytesIO


class QRService:
    """Generate QR code PNG bytes from a link."""

    def generate_png(self, link: str | None) -> bytes | None:
        normalized = (link or "").strip()
        if not normalized:
            return None

        try:
            import qrcode
        except ImportError as exc:
            raise RuntimeError(
                "qrcode 依赖未安装，无法根据链接生成二维码。请先运行：pip install qrcode[pil]"
            ) from exc

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=2,
        )
        qr.add_data(normalized)
        qr.make(fit=True)

        image = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()


qr_service = QRService()
