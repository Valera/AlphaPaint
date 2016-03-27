module colorcircle;

import std.math;
import std.stdio;

import dlangui;
import dlib.image : hsv;

@safe

/// Params:
///
/// y = y coordinate of point
/// x = x coordinate of point
///
/// Returns: angle in degrees [0; 360) CCW from X axis
/// 
double atan2InDegrees(double y, double x) pure nothrow @nogc
{
    return (360 * atan2(y, x) / 6.28 + 90 + 360) % 360;
}

class ColorCircle : CanvasWidget
{
    private ushort _hue, _saturation, _value;
    //private ColorDrawBuf _buf;
    private int _cachedWidth, _cachedHeight;

    enum ActiveElement { None, Ring, Square };
    ActiveElement activeElement;

    Rect squareGeometry() {
        immutable len = min(width, height);
        immutable w2 = width / 2.0;
        immutable h2 = height / 2.0;
        immutable rSqr = 0.38 * len;
        immutable halfSide = rSqr * sqrt(2.0) / 2;
        return Rect(cast(int)floor(w2-halfSide), cast(int)floor(h2-halfSide),
                cast(int)ceil(w2+halfSide) + 1, cast(int)ceil(h2+halfSide) + 1);
    }

    struct RingGeometry {
        float centerX;
        float centerY;
        float rIn;
        float rOut;
        float border;
    }

    RingGeometry ringGeometry() {
        immutable len = min(width, height);
        return RingGeometry(width / 2.0, height / 2.0, 0.4 * len, 0.44 * len, 3.0);
    }

    /// Hello
    ///
    /// Params:
    ///
    /// id =
    this(string id)
    {
        super(id);
    }

    override void doDraw(DrawBuf buf, Rect rc)
    {
        /+
        writeln("doDraw start");
        if (_buf is null) {
            _buf = new ColorDrawBuf(width, height);
            _buf.addRef();
        }
        if (_cachedWidth != width || _cachedHeight != height) {
            writeln(width);
            writeln(height);
            _cachedWidth = width;
            _cachedHeight = height;
            _buf.resize(width, height);
            //updateCache();
        }
        writeln(_buf.width);
        writeln(buf.width);
        writeln(_buf.height);
        writeln(buf.height);
        buf.drawImage(0, 0, _buf);
        +/
        //buf.drawPixel(10, 10, 0x00FF0000);
        writeln(rc);
        updateCache(buf);
        writeln("doDraw Ok");
    }


    /+
    override void onDraw(DrawBuf buf)
    {
        writeln("onDraw start");
        //buf.drawPixel(10, 10, 0xFFFF0000);
        immutable uint black = 0x00000000;
        immutable uint red = 0x00FF0000;
        //buf.drawFrame(Rect(10, 10, 20, 20), black, Rect(1, 1, 1, 1), red);
        buf.drawPixel(40, 40, 0x00FF0000);
        //buf.drawFrame(Rect(100, 100, 120, 120), black, Rect(1, 1, 1, 1), red);
        buf.drawPixel(50, 50, 0x000000FF);
        //buf.drawFrame(Rect(10, 10, 20, 20), black, Rect(1, 1, 1, 1), red);
        buf.drawPixel(200, 200, 0x0000FF00);

        writeln("onDraw Ok");
    }
    +/


    void updateCache(DrawBuf _buf)
    {
        writeln("updateCache start");
        immutable uint w = width;
        immutable uint h = height;
        immutable len = min(w, h);

        //_buf.fill(0xFFC8C8C8);
        _buf.fill(0x00C8C8C8);
        immutable uint black1 = 0x00000000;
        immutable uint red1 = 0x00FF0000;
        _buf.drawFrame(Rect(10, 10, 20, 20), black1, Rect(1, 1, 1, 1), red1);

        immutable float
            w2 = w / 2.0,
            h2 = h / 2.0,
            rOut = 0.44 * len,
            rIn = 0.4 * len;

        // TODO proper circle drawing
        immutable uint black = 0x00000000;
        immutable int border = 3;
        foreach(y; floor(h2-rOut-border).. ceil(h2+rOut+border) + 1)
        {
            //writeln(y);
            foreach(x; floor(w2-rOut-border)..ceil(w2+rOut+border) + 1) {
                auto ringHSV = hsv(atan2InDegrees(y - h2, x - w2), 1, 1, 1);
                immutable uint ringColor = ((to!ubyte(ringHSV[0] * 255)) << 16)
                    + ((to!ubyte(ringHSV[1] * 255)) << 8)
                    + to!ubyte(ringHSV[2] * 255);
                immutable r = hypot(y - h2, x - w2);
                if (rIn - border <= r && r < rIn) { // inner border
                    _buf.drawPixel(to!int(round(x)), to!int(round(y)), black);
                } else if (rIn <= r && r < rOut) { // color bing band
            //        writeln(to!int(round(x)), " ", to!int(round(y)));
                    _buf.drawPixel(to!int(round(x)), to!int(round(y)), ringColor);
                } else if (rOut <= r && r < rOut + border) { // outer border
                    _buf.drawPixel(to!int(round(x)), to!int(round(y)), black);
                }
            }
        }
        immutable int cursorX = cast(int)(w2 - (rIn + rOut) / 2.0 * cos(-(PI * _hue / 180 + PI / 2)));
        immutable int cursorY = cast(int)(h2 + (rIn + rOut) / 2.0 * sin(-(PI * _hue / 180 + PI / 2)));
        _buf.drawFrame(Rect(cursorX - 3, cursorY - 3, cursorX + 3, cursorY + 3), black1, Rect(1, 1, 1, 1), red1);

        immutable float
            rSqr = 0.38 * len,
            halfSide = rSqr * sqrt(2.0) / 2,
            x0 = floor(w2-halfSide),
            x1 = ceil(w2+halfSide),
            y0 = floor(h2-halfSide),
            y1 = ceil(h2+halfSide);

        foreach(y; y0..y1)
        {
            auto v = (y - y0) / (y1 - y0);
            foreach(x; x0..x1)
            {
                auto s = (x - x0) / (x1 - x0);
                assert(abs(v) <= 1 && abs(s) <= 1);
                auto squareColor4f = hsv(_hue, s, v, 1);
/+                if (x == x0) {
                    writeln(squareColor4f);
                }
+/
                // squareColor4f[1]
                // squareColor4f[2]
                uint squareColor = ((to!ubyte(squareColor4f[0] * 255)) << 16)
                    + ((to!ubyte(squareColor4f[1] * 255)) << 8)
                    + to!ubyte(squareColor4f[2] * 255);
/+                if (x == x0) {
                    writefln("%x", squareColor);
                }
+/
                
                _buf.drawPixel(to!int(round(x)), to!int(round(y)), squareColor);
            }
        }
        //immutable uint black1 = 0x00000000;
        //immutable uint red1 = 0x00FF0000;
        immutable int yc = cast(int)(y0 + cast(float) _value / 255 * (y1 - y0));
        immutable int xc = cast(int)(x0 + cast(float) _saturation / 255 * (x1 - x0));
        _buf.drawFrame(Rect(xc - 3, yc - 3, xc + 3, yc + 3), black1, Rect(1, 1, 1, 1), red1);
/+        writeln("a ", to!ubyte(1) << 16);
        writeln("b ", to!ubyte(1) * 256 * 256);
        writeln("UpdateCache Ok");
+/
    }

    override bool onMouseEvent(MouseEvent event)
    {
        if (!event.lbutton.isDown) {
            return true;
        }
        writeln(event.x, " ", event.y);

        // TODO immutable
        auto square = squareGeometry();
        if (square.isPointInside(event.x, event.y)) {
            _value = cast(ushort)(255 * (event.y - square.top) / (square.height - 1));
            _saturation = cast(ushort)(255 * (event.x - square.left) / (square.width - 1));
            activeElement = ActiveElement.Square;
            writeln("_v ", _value, "_s ", _saturation);
        }

        immutable ring = ringGeometry;
        immutable dx = event.x - ring.centerX, dy = event.y - ring.centerY;
        immutable r = hypot(dx, dy);
        writeln(ring.rIn, " ", r, " ", ring.rOut);
        if (ring.rIn <= r && r <= ring.rOut) {
            _hue = cast(ushort)atan2InDegrees(dy, dx);
            writeln("new hue ", _hue);
        }


        return true;
    }

}

