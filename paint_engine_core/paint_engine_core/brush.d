module brush;

import engine;
import std.math;
import std.algorithm;
import std.stdio;

class SimpleBrush
{
	unittest {
		auto b = new SimpleBrush(10, Type.Square, 2);
		assert(b.brushMask.alpha(0, 0) == 1);
		auto b1 = new SimpleBrush(10, Type.RoundHard, 2);
		//b1.brushMask.debugPrint();
		assert(b1.brushMask.alpha(0, 0) == 0);
		assert(b1.brushMask.alpha(4, 5) == 1);
		auto b2 = new SimpleBrush(10, Type.RoundSmooth, 2);
		assert(b1.brushMask.alpha(0, 0) == 0);
		assert(b1.brushMask.alpha(4, 5) > 0.9);
		assert(approxEqual(b1.brushMask.alpha(4, 2),b1.brushMask.alpha(4, 7)));
	}
	invariant {
		assert(width == offsetX * 2 + 1);
		assert(height == offsetY * 2 + 1);
	}

	enum Type { Square, RoundHard, RoundSmooth };
	this(float size, Type type, float spacing, float opacity = 1.0)
	{
		this.spacing = spacing;
		uint sz = (cast(int) ceil(size)) + !((cast(int) ceil(size)) % 2); // round size to nearby odd integer.
		width = sz;
		height = sz;
		offsetX = sz / 2;
		offsetY = sz / 2;
		brushMask = new AlphaMask(width, height);
		auto radius = size / 2;
		//writeln(radius);
		foreach(y; 0..height) {
			foreach(x; 0..width) {
				auto dx = x + 0.5 - width / 2.0;
				auto dy = y + 0.5 - height / 2.0;
				final switch (type)
				{
					case Type.Square:
						brushMask.alpha(x, y) = opacity;
						break;
					case Type.RoundHard:
						if (pow(dx, 2) + pow(dy, 2) < radius * radius) {
							brushMask.alpha(x, y) = opacity;
						} else {
							brushMask.alpha(x, y) = 0;
						}
						break;
					case Type.RoundSmooth:
					{
						float r = hypot(dx, dy);
						if (r > radius) {
							brushMask.alpha(x, y) = 0;
						} else {
							brushMask.alpha(x, y) = opacity * r / radius;
						}
						break;
					}
				}
			}
		}
	}
	BrushDub colorDub(Color color)
	{
		BrushDub dub = new BrushDub(width, height);
		foreach(y; 0..height) {
			foreach(x; 0..width) {
				dub.setPixel(x, y, brushMask.alpha(x, y) * color);
			}
		}
		return dub;	
	}
private:
	uint offsetX, offsetY;
	uint width, height;
	AlphaMask brushMask;
	float opacity;
	float spacing;
}

/**
 * Class for individual brush stokes
 * 
 * Create new instance when brush settings change.
 */
class BrushStroke
{
	/**
	 * Typical usage example
	 */
	unittest {
		Color c;
		assert(c.r == 0 && c.g == 0 && c.b == 0);
		SimpleBrush brush = new SimpleBrush(10, SimpleBrush.Type.RoundHard, 8);
		Image image = new Image(20, 20);
		//writeln(image.pixel(10, 10));
		BrushStroke bs = new BrushStroke(brush, image, Color(1, 0, 0));
		//brush.brushMask.debugPrint();
		//image.debugPrint();
		bs.processMouseMove(10, 10, 0.01);
		//image.debugPrint();
		//writeln(image.pixel(10, 10));
		bs.processMouseMove(20, 20, 0.01);
		//image.debugPrint();
		assert(image.pixel(10, 10) == Color(1, 0, 0));
	}

	/**
	 * Another typical usage example. Three buds should be
	 * drawn at known places. Result is verified vs fixed
	 * expected pixel map.
	 */
	unittest {
		SimpleBrush brush = new SimpleBrush(2.5, SimpleBrush.Type.RoundHard, 2);
		Image image = new Image(5, 5);
		BrushStroke bs = new BrushStroke(brush, image, Color(1, 0, 0));
		//brush.brushMask.debugPrint();
		bs.processMouseMove(0, 0, 0.01);
		//image.debugPrint();
		bs.processMouseMove(0, 2, 0.01);
		//image.debugPrint();
		bs.processMouseMove(2, 2, 0.01);
		//image.debugPrint();
		Color r = Color(1, 0, 0), b = Color(0, 0, 0);
		Color expected[5][5] = [
			[r, r, b, b, b],
			[r, b, r, b, b],
			[r, r, r, r, b],
			[r, b, r, b, b],
			[b, b, b, b, b]];
		foreach(y; 0..5){
			foreach(x; 0..5) {
				assert(expected[y][x] == image.pixel(x, y));
			}
		}
	}
	/**
	 * ctor
	 */
	this(SimpleBrush brush, Image image, Color color)
	{
		this.brush = brush;
		brushDub = brush.colorDub(color);
		this.image = image;
		this.transaction = image.startPaintTransaction();
	}

	/**
	 * Draws several brush dubs along brush trajectory up to (x, y)
	 * point
	 * 
	 * Returns:
	 *   image region that was updated and UI should redraw.
	 */
	Rect processMouseMove(float x, float y, float pressure)
	{
		if (!interpolator) {
			this.interpolator = new StrokeInterpolator(brush.spacing, x, y, pressure);
		}
		interpolator.mouseInput(x, y, pressure);
		return drawBrushTrace();
	}
	/**
	 * forget about previous stroke and be ready to start new one
	 */
	void reset()
	{
		this.interpolator = null;
	}
private:
	Rect drawBrushTrace()
	{
		Rect boundingRect;
		bool first = true;
		foreach(values; interpolator.interpolatedValues) {
			auto xCenter = values[0];
			auto yCenter = values[1];
			auto pressure = values[2];
			auto xDraw = cast(int)round(xCenter - brush.offsetX);
			auto yDraw = cast(int)round(yCenter - brush.offsetY);
			//writeln("drawing dub at", xDraw, " ", yDraw);
			transaction.drawOnPainting(brushDub, brush.brushMask, xDraw, yDraw);
			Rect brushRect = Rect(xDraw, yDraw, brush.width, brush.height);
			if (first) {
				boundingRect = brushRect;
			} else {
				boundingRect = boundingRect.boundingRect(brushRect);
			}
		}
		transaction.displayChanges();
		return boundingRect;
	}

	Color color;
	SimpleBrush brush;
	BrushDub brushDub;
	Image image;
	PaintTransaction transaction;
	StrokeInterpolator interpolator;
}

/**
 * StrokeInterpolator generates intermeditate points and pressure values
 * between incoming stylus positions.
 * 
 * [x, y, pressure] intermediate positions are stored in property and
 * distributed evenly along stylus curve with spacing
 */
class StrokeInterpolator
{
	unittest {
		auto stroke = new StrokeInterpolator(5 * SQRT2, 10, 10, 0);
		assert(stroke.interpolatedValues == [[10, 10, 0]]);
		stroke.mouseInput(20, 20, 1);
		//assert(stroke.interpolatedValues == []);
		assert(stroke.interpolatedValues == [[10.0, 10.0, 0.0], [15, 15, 0.5], [20.0, 20, 1]]);
		
		stroke.mouseInput(21, 21, 1);
		assert(stroke.interpolatedValues == [[10.0, 10.0, 0.0], [15, 15, 0.5], [20.0, 20, 1]]);
		assert(approxEqual(stroke.offset, -SQRT2));
		assert(approxEqual(stroke.prevX, 21));
		assert(approxEqual(stroke.prevY, 21));
		stroke.mouseInput(26, 26, 0);
		assert(stroke.interpolatedValues.length == 4 &&
		       approxEqual(stroke.interpolatedValues[$-1][], [25, 25, 0.2]));
		
		stroke.mouseInput(31, 31, 1);
		//writeln(stroke.interpolatedValues);
		assert(stroke.interpolatedValues.length == 5 &&
		       approxEqual(stroke.interpolatedValues[$-1][], [30.0, 30, 0.8]));
		
		stroke.interpolatedValues = [];
		stroke.mouseInput(51, 51, 1);
		
		assert(stroke.interpolatedValues.length == 4 &&
		       approxEqual(stroke.interpolatedValues[0][], [35.0, 35, 1]) &&
		       approxEqual(stroke.interpolatedValues[1][], [40.0, 40, 1]) &&
		       approxEqual(stroke.interpolatedValues[2][], [45.0, 45, 1]) &&
		       approxEqual(stroke.interpolatedValues[3][], [50.0, 50, 1]));
	}
	/**
	 * Initialize Object with spacing and starting values of pressure and
	 * coordintates.
	 */
	this(float spacing, float x0, float y0, float pressure)
	{
		this.prevX = x0;
		this.prevY = y0;
		prevPressure = pressure;
		startInd = 1;
		this.spacing = spacing;
		offset = 0;
		interpolatedValues ~= [x0, y0, pressure];
	}
	/**
	 * Generate intermeditate points to the given values.
	 */
	void mouseInput(float x, float y, float pressure)
	{
		auto dx = x - prevX;
		auto dy = y - prevY;
		auto dPressure = pressure - prevPressure;
		auto length = hypot(dx, dy);
		
		if (length == 0)
			return;
		
		if (length < offset) {
			offset -= length;
			prevX = x;
			prevY = x;
			prevPressure = pressure;
			return;
		}
		
		auto count = cast(uint) ((length - offset) / spacing);
		//writefln("%s %s %s %s\n", count, length, offset, spacing);
		auto x0 = prevX + offset * dx / length;
		auto y0 = prevY + offset * dy / length;
		auto pressure0 = prevPressure + offset * dPressure / length;
		foreach(i; startInd..count + 1) {
			auto interpolationParam = i * spacing / length;
			auto x1 = x0 + dx * interpolationParam;
			auto y1 = y0 + dy * interpolationParam;
			//writeln(interpolationParam, x1, y1, prevPressure, pressure);
			auto pressure1 = pressure0 + dPressure * interpolationParam;
			interpolatedValues ~= [x1, y1, pressure1];
		}
		offset = count * spacing + offset - length;
		startInd = 1;
		prevX = x;
		prevY = y;
		prevPressure = pressure;
	}
	void finalize()
	{
	}
public:
	float[3][] interpolatedValues; /// Intermeditate [x, y, pressure] values.
private:
	float prevX, prevY, prevPressure, offset;
	float spacing;
	uint startInd;
}
