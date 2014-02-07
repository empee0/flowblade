

import gtk
import math


from cairoarea import CairoDrawableArea
import gui
import respaths
import viewgeom

SHADOW = 0
MID = 1
HI = 2

ACTIVE_RING_COLOR = (0.0, 0.0, 0.0)
DEACTIVE_RING_COLOR = (0.6, 0.6, 0.6)

ACTIVE_SHADOW_COLOR = (0.1, 0.1, 0.1)
ACTIVE_MID_COLOR = (0.5, 0.5, 0.5)
ACTIVE_HI_COLOR = (1.0, 1.0, 1.0)

DEACTIVE_SHADOW_COLOR = (0.6, 0.6, 0.6)
DEACTIVE_MID_COLOR = (0.7, 0.7, 0.7)
DEACTIVE_HI_COLOR = (0.85, 0.85, 0.85)

BOX_BG_COLOR = (1, 1, 1)
LINE_COLOR = (0, 0, 0)

def _draw_band_select_circle(cr, x, y, band_color, ring_color):
    radius = 6
    small_radius = 4
    pad = 6
    degrees = math.pi / 180.0

    cr.set_source_rgb(*ring_color)
    cr.move_to(x + pad, y + pad)
    cr.arc (x + pad, y + pad, radius, 0.0 * degrees, 360.0 * degrees)
    cr.fill()
    
    cr.set_source_rgb(*band_color)
    cr.move_to(x + pad, y + pad)
    cr.arc (x + pad, y + pad, small_radius, 0.0 * degrees, 360.0 * degrees)
    cr.fill()


class ColorWheel:

    def __init__(self):
        self.band = SHADOW
        
        self.widget = CairoDrawableArea(260, 
                                        260, 
                                        self._draw)
        self.widget.press_func = self._press_event
        self.widget.motion_notify_func = self._motion_notify_event
        self.widget.release_func = self._release_event
        self.X_PAD = 3
        self.Y_PAD = 3
        self.CENTER_X = 130
        self.CENTER_Y = 130
        self.CIRCLE_HALF = 6
        self.cursor_x = self.CENTER_X
        self.cursor_y = self.CENTER_Y
        self.WHEEL_IMG = gtk.gdk.pixbuf_new_from_file(respaths.IMAGE_PATH + "color_wheel.png")
        self.MAX_DIST = 123
        self.shadow_x = self.CENTER_X
        self.shadow_y = self.CENTER_Y
        self.mid_x = self.CENTER_X
        self.mid_y = self.CENTER_Y
        self.hi_x = self.CENTER_X
        self.hi_y = self.CENTER_Y

    def set_band(self, band):
        self.band = band
        if self.band == SHADOW:
            self.cursor_x = self.shadow_x
            self.cursor_y = self.shadow_y
        elif self.band == MID:
            self.cursor_x = self.mid_x
            self.cursor_y = self.mid_y
        else:
            self.cursor_x = self.hi_x
            self.cursor_y = self.hi_y 

    def _press_event(self, event):
        """
        Mouse button callback
        """
        self.cursor_x, self.cursor_y = self._get_legal_point(event.x, event.y)
        self._save_point()
        self.widget.queue_draw()

    def _motion_notify_event(self, x, y, state):
        """
        Mouse move callback
        """
        self.cursor_x, self.cursor_y = self._get_legal_point(x, y)
        self._save_point()
        self.widget.queue_draw()
        
    def _release_event(self, event):
        self.cursor_x, self.cursor_y = self._get_legal_point(event.x, event.y)
        self._save_point()
        self.widget.queue_draw()
        
    def _get_legal_point(self, x, y):
        vec = viewgeom.get_vec_for_points((self.CENTER_X, self.CENTER_Y), (x, y))
        dist = vec.get_length()
        if dist < self.MAX_DIST:
            return (x, y)

        new_vec = vec.get_multiplied_vec(self.MAX_DIST / dist )
        return new_vec.end_point
    
    def _save_point(self):
        if self.band == SHADOW:
            self.shadow_x = self.cursor_x 
            self.shadow_y = self.cursor_y
        elif self.band == MID:
            self.mid_x = self.cursor_x 
            self.mid_y = self.cursor_y
        else:
            self.hi_x = self.cursor_x
            self.hi_y = self.cursor_y
        
    def _draw(self, event, cr, allocation):
        """
        Callback for repaint from CairoDrawableArea.
        We get cairo context and allocation.
        """
        x, y, w, h = allocation
       
        # Draw bg
        cr.set_source_rgb(*(gui.bg_color_tuple))
        cr.rectangle(0, 0, w, h)
        cr.fill()

        cr.set_source_pixbuf(self.WHEEL_IMG, self.X_PAD, self.Y_PAD)
        cr.paint()

        _draw_band_select_circle(cr, self.shadow_x - self.CIRCLE_HALF, self.shadow_y - self.CIRCLE_HALF, 
                                 DEACTIVE_SHADOW_COLOR, DEACTIVE_RING_COLOR)
        _draw_band_select_circle(cr, self.mid_x - self.CIRCLE_HALF, self.mid_y - self.CIRCLE_HALF,
                                 DEACTIVE_MID_COLOR, DEACTIVE_RING_COLOR)
        _draw_band_select_circle(cr, self.hi_x - self.CIRCLE_HALF, self.hi_y - self.CIRCLE_HALF,
                                 DEACTIVE_HI_COLOR, DEACTIVE_RING_COLOR)
        
        if self.band == SHADOW:
            band_color = ACTIVE_SHADOW_COLOR
        elif self.band == MID:
            band_color = ACTIVE_MID_COLOR
        else:
            band_color = ACTIVE_HI_COLOR
        
        _draw_band_select_circle(cr, self.cursor_x - self.CIRCLE_HALF, self.cursor_y - self.CIRCLE_HALF, band_color, ACTIVE_RING_COLOR)


class ColorBandSelector:
    def __init__(self):
        self.band = SHADOW

        self.widget = CairoDrawableArea(42, 
                                        18, 
                                        self._draw)

        self.widget.press_func = self._press_event
        self.SHADOW_X = 0
        self.MID_X = 15
        self.HI_X = 30
        
        self.band_change_listener = None # monkey patched in at creation site
    
    def _press_event(self, event):
        x = event.x
        y = event.y
        
        if self._circle_hit(self.SHADOW_X, x, y):
            self.band_change_listener(SHADOW)
        elif self._circle_hit(self.MID_X, x, y):
            self.band_change_listener(MID)
        elif self._circle_hit(self.HI_X, x, y):
             self.band_change_listener(HI)

    def _circle_hit(self, band_x, x, y):
        if x >= band_x and x < band_x + 12:
            if y > 0 and y < 12:
                return True
        
        return False

    def _draw(self, event, cr, allocation):
        """
        Callback for repaint from CairoDrawableArea.
        We get cairo context and allocation.
        """
        x, y, w, h = allocation
       
        # Draw bg
        cr.set_source_rgb(*(gui.bg_color_tuple))
        cr.rectangle(0, 0, w, h)
        cr.fill()
        
        ring_color = (0.0, 0.0, 0.0)
        _draw_band_select_circle(cr, self.SHADOW_X, 0, (0.1, 0.1, 0.1), ring_color)
        _draw_band_select_circle(cr, self.MID_X, 0, (0.5, 0.5, 0.5), ring_color)
        _draw_band_select_circle(cr, self.HI_X, 0, (1.0, 1.0, 1.0), ring_color)

        self._draw_active_indicator(cr)
    
    def _draw_active_indicator(self, cr):
        y = 14.5
        HALF = 4.5
        HEIGHT = 2

        if self.band == SHADOW:
            x = self.SHADOW_X + 1.5
        elif self.band == MID:
            x = self.MID_X + 1.5
        else:
            x = self.HI_X + 1.5

        cr.set_source_rgb(0, 0, 0)
        cr.move_to(x, y)
        cr.line_to(x + 2 * HALF, y)
        cr.line_to(x + 2 * HALF, y + HEIGHT)
        cr.line_to(x, y + HEIGHT)
        cr.close_path()
        cr.fill()


class ColorCorrector:
    def __init__(self, slider_rows):
        self.band = SHADOW
        
        self.widget = gtk.VBox()

        self.color_wheel = ColorWheel()
        self.band_selector = ColorBandSelector()
        self.band_selector.band_change_listener = self._band_changed

        lift_slider_row = slider_rows[0]
        gain_slider_row = slider_rows[1]
        gamma_slider_row = slider_rows[2]

        band_row = gtk.HBox()
        band_row.pack_start(gtk.Label(), True, True, 0)
        band_row.pack_start(self.band_selector.widget, False, False, 0)
        band_row.pack_start(gtk.Label(), True, True, 0)

        wheel_row = gtk.HBox()
        wheel_row.pack_start(gtk.Label(), True, True, 0)
        wheel_row.pack_start(self.color_wheel.widget, False, False, 0)
        wheel_row.pack_start(gtk.Label(), True, True, 0)

        self.widget.pack_start(band_row, True, True, 0)
        self.widget.pack_start(wheel_row, False, False, 0)
        self.widget.pack_start(lift_slider_row, False, False, 0)
        self.widget.pack_start(gain_slider_row, False, False, 0)
        self.widget.pack_start(gamma_slider_row, False, False, 0)

    def _band_changed(self, band):
        self.band = band
        self.color_wheel.set_band(band)
        self.band_selector.band = band
    
        self.band_selector.widget.queue_draw()
        self.color_wheel.widget.queue_draw()



class BoxEditor:
    
    def __init__(self, pix_size, value_size, listener):

        self.pix_size = pix_size;
        self.value_size = value_size;
        self.pix_per_val = value_size / pix_size
        self.off_x = 1
        self.off_y = 1
        self.listener = listener;

        self.widget = CairoDrawableArea(self.pix_size + 2, 
                                        self.pix_size + 2, 
                                        self._draw)
        self.widget.press_func = self._press_event
        self.widget.motion_notify_func = self._motion_notify_event
        self.widget.release_func = self._release_event

    def get_box_val_point(self, x, y):
        # calculate value
        px = int((x - self.off_x) * self.pix_per_val)
        py = int((self.pix_size - (y - self.off_y)) * self.pix_per_val)

        # force range
        if px < 0:
            px = 0
        if py < 0:
            py = 0
        if px >= self.value_size:
            px = self.value_size - 1
        if py >= self.value_size:
            py = self.value_size - 1

        return (px, py)

    """
    def get_box_panel_point(p, x, y):

        p.x = (int) (x / pixPerVal) + offX;
        p.y = pixSize - (int) (y / pixPerVal) + offY;

    """       
    def _press_event(self, event):
        p = self.get_box_val_point(event.x, event.y)
        self.listener.box_mouse_value_update(p)

    def _motion_notify_event(self, x, y, state):
        p = self.get_box_val_point(x, y)
        self.listener.box_mouse_value_update(p)
        
    def _release_event(self, event):
        p = self.get_box_val_point(event.x, event.y)
        self.listener.box_mouse_value_update(p)

    def _draw(self, event, cr, allocation):
        x, y, w, h = allocation
       
        # Draw bg
        cr.set_source_rgb(*(gui.bg_color_tuple))
        cr.rectangle(0, 0, w, h)
        cr.fill()
        
        cr.set_source_rgb(*BOX_BG_COLOR )
        cr.rectangle(0, 0, self.pix_size + 1, self.pix_size + 1)
        cr.fill_preserve()
        
        cr.set_source_rgb(*LINE_COLOR)
        cr.stroke()

        # value lines
        step = self.pix_size / 4
        cr.set_line_width(1.0)
        for i in range(1, 4):
            cr.move_to(step * i, 0) 
            cr.line_to(step * i, self.pix_size)
            cr.stroke()

        for i in range(1, 4):
            cr.move_to(0, step * i) 
            cr.line_to(self.pix_size, step * i)
            cr.stroke()


class CurvesEditor:
    
    def __init__(self):
        self.widget = gtk.VBox()
        self.box_exitor = BoxEditor(256, 1.0, self)

        box_row = gtk.HBox()
        box_row.pack_start(gtk.Label(), True, True, 0)
        box_row.pack_start(self.box_exitor.widget, False, False, 0)
        box_row.pack_start(gtk.Label(), True, True, 0)

        self.widget.pack_start(box_row, True, True, 0)

    def box_mouse_value_update(self, p):
        print p