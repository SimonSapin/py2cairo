'''test pycairo API
- can be expanded later as required.
- is not able to test the quality of images created. We assume cairo itself
  tests for this.
'''
from __future__ import division        # new in 2.2, redundant in 3.0
from __future__ import absolute_import # new in 2.5, redundant in 2.7/3.0
from __future__ import print_function  # new in 2.6, redundant in 3.0

import io
import tempfile as tfi

import cairo
import py.test as test


def test_context():
  if cairo.HAS_IMAGE_SURFACE:
    f, w, h = cairo.FORMAT_ARGB32, 100, 100
    s = cairo.ImageSurface(f, w, h)
    ctx = cairo.Context(s)
    ctx.set_source_rgb(1.0, 1.0, 1.0)
    ctx.set_operator(cairo.OPERATOR_SOURCE)
    ctx.paint()


def test_matrix():
  m = cairo.Matrix()
  m.rotate(10)
  m.scale(1.5, 2.5)
  m.translate(10, 20)


def test_path():
  # AttributeError: 'module' object has no attribute 'Path'
  test.raises(AttributeError, "p = cairo.Path()")
  # see examples/warpedtext.py


def test_pattern():
  # TypeError: The Pattern type cannot be instantiated
  test.raises(TypeError, "p = cairo.Pattern()")

  r,g,b,a = 0.1, 0.2, 0.3, 0.4
  p = cairo.SolidPattern(r,g,b,a)
  assert p.get_rgba() == (r,g,b,a)

  # SurfacePattern

  # TypeError: The Gradient type cannot be instantiated
  test.raises(TypeError, "p = cairo.Gradient()")

  x0,y0,x1,y1 = 0.0, 0.0, 0.0, 1.0
  p = cairo.LinearGradient(x0,y0,x1,y1)
  assert p.get_linear_points() == (x0,y0,x1,y1)
  p.add_color_stop_rgba(1, 0, 0, 0, 1)
  p.add_color_stop_rgba(0, 1, 1, 1, 1)

  cx0, cy0, radius0, cx1, cy1, radius1 = 1.0, 1.0, 1.0, 2.0, 2.0, 1.0
  p = cairo.RadialGradient(cx0, cy0, radius0, cx1, cy1, radius1)
  assert p.get_radial_circles() == (cx0, cy0, radius0, cx1, cy1, radius1)
  p.add_color_stop_rgba(0, 1, 1, 1, 1)
  p.add_color_stop_rgba(1, 0, 0, 0, 1)


def test_surface():
  # TypeError: The Surface type cannot be instantiated
  test.raises(TypeError, "s = cairo.Surface()")

  if cairo.HAS_IMAGE_SURFACE:
    f, w, h = cairo.FORMAT_ARGB32, 100, 100
    s = cairo.ImageSurface(f, w, h)
    assert s.get_format() == f
    assert s.get_width()  == w
    assert s.get_height() == h

  if cairo.HAS_PDF_SURFACE:
    f, w, h = tfi.TemporaryFile(mode='w+b'), 100, 100
    s = cairo.PDFSurface(f, w, h)

  if cairo.HAS_PS_SURFACE:
    f, w, h = tfi.TemporaryFile(mode='w+b'), 100, 100
    s = cairo.PSSurface(f, w, h)

  if cairo.HAS_RECORDING_SURFACE:
    s = cairo.RecordingSurface(cairo.CONTENT_COLOR, None)
    s = cairo.RecordingSurface(cairo.CONTENT_COLOR, (1,1,10,10))

  if cairo.HAS_SVG_SURFACE:
    f, w, h = tfi.TemporaryFile(mode='w+b'), 100, 100
    s = cairo.SVGSurface(f, w, h)


def test_text():
  pass


def test_mime_data():
    # A 1x1 pixel white image:
    png_bytes = (
        b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAAAAAA6fptVAAAACklEQV'
        b'QI12P4DwABAQEAG7buVgAAAABJRU5ErkJggg=='.decode('base64'))
    jpeg_bytes = (
        b'eJz7f+P/AwYBLzdPNwZGRkYGDyBk+H+bwRnEowj8P8TAzcHACDJHkOH/EQYRIBsV'
        b'cP6/xcDBCBJlrLcHqRBAV8EAVcHIylSPVwGbPQEFjPaK9XDrBAipBSq4CQB9jiS0'
        .decode('base64').decode('zlib'))

    def render(image, surface_type):
        file_like = io.BytesIO()
        surface = surface_type(file_like, 100, 100)
        context = cairo.Context(surface)
        context.set_source_surface(image, 0, 0)
        context.paint()
        surface.finish()
        pdf_bytes = file_like.getvalue()
        return pdf_bytes

    image = cairo.ImageSurface.create_from_png(io.BytesIO(png_bytes))
    assert image.get_mime_data('image/jpeg') is None

    pdf_bytes = render(image, cairo.PDFSurface)
    assert pdf_bytes.startswith(b'%PDF')
    assert b'/Filter /DCTDecode' not in pdf_bytes

    image.set_mime_data('image/jpeg', jpeg_bytes)
    jpeg_bytes = jpeg_bytes[:]  # Copy, drop a reference to the old object.
    assert image.get_mime_data('image/jpeg')[:] == jpeg_bytes

    pdf_bytes = render(image, cairo.PDFSurface)
    assert pdf_bytes.startswith(b'%PDF')
    # JPEG-encoded image:
    assert b'/Filter /DCTDecode' in pdf_bytes

    image.set_mime_data('image/jpeg', None)
    assert image.get_mime_data('image/jpeg') is None
