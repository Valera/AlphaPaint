module engine;

import std.stdio;
import std.array;
import std.algorithm;
import std.math;
import std.bitmanip;

import std.exception;

struct Rect
{
	int x, y;
	uint width, height;
	Rect boundingRect(Rect other)
	{
		return Rect(min(x, other.x), min(y, other.y),
		            max(x + width, other.x + other.width), max(y + height, other.y + other.height));
	}
}

enum tilesize = 16;
alias Color[16][16] PixelTile;
alias float[16][16] AlphaTile;

enum CompositionMode
{
	Normal,
	Multiply
}

struct Color
{
	float r = 0;
	float g = 0;
	float b = 0;
	this (float red, float green, float blue)
	{
		r = red;
		g = green;
		b = blue;
	}
	float[3] asArray() {return [r, g, b];}
	Color opBinary(string op)(float rhs)
	{
		static if (op == "*") {
			return Color(r * rhs, g * rhs, b * rhs);
		}
	}
	Color opBinaryRight(string op)(float rhs)
	{
		static if (op == "*") {
			return Color(r * rhs, g * rhs, b * rhs);
		}
	}
}

class AlphaMask
{
	this(uint width, uint height)
	{
		this._width = width;
		this._height = height;
		alphaValues = new float[width * height];
	}
	ref float alpha (uint x, uint y)
	{
		return alphaValues[y * _width + x];
	}
	float alpha (uint x, uint y) const
	{
		return alphaValues[y * _width + x];
	}
	@property uint width() { return _width; }
	@property uint height() { return _height; }
	void debugPrint()
	{
		foreach(y; 0.._height) {
			foreach(x; 0.._width) {
				//writef("(%s,%s,%s)", pixel(x,y).r, pixel(x,y).g, pixel(x,y).b);
				if(alpha(x, y) == 0) {
					write("_");
				}else{
					write("#");
				}
			}
			writeln();
		}
		writeln();
	}
private:
	uint _width, _height;
	float[] alphaValues;
}

interface ImageInterface
{
	uint width();
	uint height();
	Color pixel(uint x, uint y);
	void setPixel(uint x, uint y, Color);
}

class History
{
	this(uint maxTransactions)
	{
		this.maxTransactions = maxTransactions;
	}
	void undo(Image image)
	{
		transactions[currTransaction--].undo();
	}
	void redo(Image image)
	{
		transactions[currTransaction++].redo();
	}
	void saveTransaction(LayerTransaction lt)
	{
		if (storedTransactions == maxTransactions) {
			transactions.remove(0);
			--storedTransactions;
			--currTransaction;
		}
		transactions[currTransaction++] = lt;
		storedTransactions = currTransaction;
	}
	invariant () {
		assert(storedTransactions <= maxTransactions);
		assert(currTransaction <= storedTransactions);
	}
private:
	uint maxTransactions;
	uint currTransaction, storedTransactions;
	LayerTransaction[] transactions;
}

class BrushDub: PixelSurface
{
	this (uint width, uint height)
	{
		pixels = new Color[width * height];
		_width = width;
		_height = height;
	}
	@property uint width() const { return _width; }
	@property uint height() const { return _height; }
	Color pixel(uint x, uint y) const
	{
		return pixels[_width * y + x];
	}
	void setPixel(uint x, uint y, Color c)
	{
		pixels[_width * y + x] = c;
	}
private:
	uint _width, _height;
	Color[] pixels;
}

/**
 * Image is smart container for layers.
 */
class Image: PixelSurface
{
	this(uint width, uint height)
	{
		baseLayer = new Layer(width, height);
		_width = width;
		_height = height;
		rendered = new Layer(width, height);
		layers = [new Layer(width, height)];
	}
	/**
	 * Save pointer to QImage's scanlines for interactive display
	 * of changes.
	 * 
	 * Caller must ensure that QImage has the same width and
	 * height as this Image.
	 */
	void register1(size_t[]scanLines)
	{
		foreach(line; scanLines) {
			ubyte *p = cast(ubyte *) line;
			writeln("#1 ", p);
			p[0..20] = 255;
		}
	}
	void register2(size_t line)
	{
		ubyte *p = cast(ubyte *) line;
		writeln("#2 ", p);
		p[0..10] = 255;
	}
	void registerQImageScanLines(size_t[]scanLines)
	{
		assert(scanLines.length == _height);
		_scanLines = new ubyte[][scanLines.length];
		foreach(i, ref line; _scanLines) {
			writeln(scanLines[i]);
			line = (cast(ubyte*)(scanLines[i]))[0.._width * 4];
		}
	}

	invariant () {
		assert(baseLayer.width == _width);
		assert(baseLayer.height == _height);
		foreach(l; layers)
		{
			assert(l.width == _width);
			assert(l.height == _height);
		}
		assert(rendered.width == _width);
		assert(rendered.height == _height);
		assert(_scanLines is null || _scanLines.length == _height);
		assert(0 <= activeLayerIndex && activeLayerIndex < layers.length);
	}
	@property uint  width() const { return _width; }
	@property uint height() const { return _height; }

	Color pixel(uint x, uint y) const
	{
		return rendered.pixel(x, y);
	}
	
	void setActiveLayer(int index)
	{
		activeLayerIndex = index;
	}
	
	// void renderTo(char *target)
	
	ulong layerCount()
	{
		return layers.length;
	}
	void addLayerOnTop()
	{
		layers ~= new Layer(width, height);         
	}
	void insertLayer(uint index, CompositionMode mode)
	{
		layers.insertInPlace(index, new Layer(width, height, mode));
	}
	void deleteLayer(uint index)
	{
		layers.remove(index);
	}
	void resize(int topExpand, int leftExpand,
	            int bottomExpand, int rightExpand,
	            Color extraSpaceFill = Color.init, float opacity = 0)
	{
		baseLayer.resize(topExpand, leftExpand, bottomExpand, rightExpand, extraSpaceFill,
		                 opacity);
		foreach(l; layers)
		{
			l.resize(topExpand, leftExpand, bottomExpand, rightExpand, extraSpaceFill,
			         opacity);
		}
		_scanLines = null;
	}
	void printHello()
	{
		writeln("Hello, username!");
	}
	
	void moveActiveLayer() {}
	
	PaintTransaction startPaintTransaction()
	{
		return new PaintTransaction(layers[activeLayerIndex], this);
	}
	void propagateLayerChanges()
	{

	}
	void debugPrint()
	{
		rendered.debugPrint();
	}
	void update()
	{
		rendered.copyFrom(baseLayer);
		foreach(layer; layers) {
			rendered.draw(layer);
		}
		rendered.drawToScanLines(_scanLines);
	}
	void update(Rect rect)
	{
		update();
	}
private:
	Layer[] layers;
	uint _width, _height, activeLayerIndex;
	Layer rendered; /// all layers rendered for display.
	Layer baseLayer;

	ubyte[][] _scanLines; /// External QImage scanlines.
	
	// add proper multithreaded locking in future.
	// Now on any operation on locked Image it produces error.
	bool locked;
}

class LayerTransaction
{
	this(Layer layer, Image image)
	{
		this.layer = layer;
		this.image = image;
		enforce(image.locked == false);
		image.locked = true;
	}
	void end()
	{
		image.locked = false;
	}
	abstract void undo();
	abstract void redo();
	abstract void optimize();
	abstract void applyFinally();
private:
	Layer layer;
	Image image;
	bool optimized;
}

class PaintTransaction: LayerTransaction
{
	this(Layer layer, Image image)
	{
		super(layer, image);
		backedTiles.length = layer.width * layer.height;
		nXTiles = layer.width / 16;
		nYTiles = layer.height / 16;
	}
	override void undo() {}
	override void redo() {}
	override void optimize() {}
	override void applyFinally() {}
	void drawOnPainting(BrushDub dub, AlphaMask mask, uint x, uint y)
	{
		// Tile backup.
		auto tileX0 = max(0, x / 16);
		auto tileY0 = max(0, y / 16);
		auto tileX1 = min(nXTiles, (x + dub.width + 15) / 16);
		auto tileY1 = min(nYTiles, (y + dub.height + 15) / 16);
		foreach(tileX; tileX0..tileX1)
		{
			foreach(tileY; tileY0..tileY1)
			{
				if (!backedTiles[tileY * nXTiles + tileX])
				{
					backedTiles[tileY * layer.width + tileX] = 1;
					tileCoords ~= [cast(ushort)tileY, cast(ushort)tileX];
					Color[16][16] newTile;
					foreach(y1; 0..16)
						foreach(x1; 0..16) {
							//writefln("%s %s %s %s\n", y1, x1, tileY, tileX);
							newTile[y1][x1] = layer.pixel(tileX * 16 + x1, tileY * 16 + y1);
						}
				}
			}
		}
		// Actual drawing
		//writeln("actual drawing dub at ", x, " ", y);
		layer.draw(dub, mask, x, y);
		//image.propogateLayerChanges(Rect(x, y, dub.width, dub.height));
	}
	void displayChanges() 
	{
		image.update(); // TODO: update bounding rect and return it. return bounding rect
	}
private:
	// TODO: ddoc
	Color [16][16][] pixelTiles;
	float [16][16][] alphaTiles;
	ushort [2][] tileCoords;
	uint nXTiles, nYTiles;
	BitArray backedTiles;
}

// TODO: work for different endianess
ubyte clampFloatColor(float colorComponent)
{
	return cast(ubyte)max(0, min(255, colorComponent * 255));
}

unittest {
	assert(clampFloatColor(0) == 0);
	assert(clampFloatColor(1) == 255);
	assert(clampFloatColor(-1) == 0);
	assert(clampFloatColor(1.01) == 255);
}

interface PixelSurface
{
	const Color pixel(uint x, uint y);
	@property const uint width();
	@property const uint height();
}

class Layer: PixelSurface {
	this(uint width, uint height, CompositionMode mode = CompositionMode.Normal)
	{
		this._width = width;
		this._height = height;
		this._mode = mode;
		this._pixels = new float[height * width * 3];
		this._pixels[] = 0;
		this._alphas = new float[height * width];
		this._alphas[] = 1;
		this._opacity = 1;
	}
	invariant {
		assert(_pixels.length == _width * _height * 3);
		assert(_alphas.length == _width * _height);
		assert(0 <= _opacity && _opacity <= 1);
	}
	void copyFrom(const Layer other)
	{
		_width = other._width;
		_height = other.height;
		_mode = mode;
		_pixels.length = _height * _width * 3;
		_alphas.length = _height * _width;
		_pixels[] = other._pixels[];
		_alphas[] = other._alphas[];
		_opacity = other._opacity;
	}
	void debugPrint()
	{
		write("   ");
		foreach(x; 0.._width) {
			if (x %5 == 0) {
				writef("%-5s", x);
			}
		}
		writeln();
		foreach(y; 0.._height) {
			writef("%2s ", y);
			foreach(x; 0.._width) {
				//writef("(%s,%s,%s)", pixel(x,y).r, pixel(x,y).g, pixel(x,y).b);
				if(pixel(x, y) == Color(0, 0, 0)) {
					write("_");
				}else{
					write("#");
				}
			}
			writeln();
		}
		writeln();
	}
	void draw(const Layer other) {
		enforce(_width == other._width && _height == other.height);
		final switch (_mode) {
			case CompositionMode.Normal:
				this._pixels[] = (cast (const float[]) _pixels[]) * (1 - other._opacity)
					+ other._pixels[] * other._opacity;
				//this._pixels[] += ;
				break;
			case CompositionMode.Multiply:
				// FIXME no opacity support
				this._pixels[] *= other._pixels[] ;
				break;
		}
	}
	void draw(const PixelSurface other, const AlphaMask mask, uint x0, uint y0) {
		//auto xmax = min(_width, x0 + other.width);
		//auto ymax = min(_height, y0 + other.height);
		foreach(y1; 0..other.height) {
			if (y1 + y0 < 0 || y1 + y0 >= height)
				continue;
			foreach(x1; 0..other.width) {
				if (x1 + x0 < 0 || x1 + x0 >= height)
					continue;
				auto baseOffset = 3 * ((y0 + y1) * _width + x0 + x1);
				_pixels[baseOffset..baseOffset + 3] =
					_pixels[baseOffset..baseOffset + 3] * (mask.alpha(x1, y1) - 1)
					+ mask.alpha(x1, y1) * other.pixel(x1, y1).asArray()[];
				//assert(pixel(x0 + x1, y0 + y1) == other.pixel(x1, y1));
			}
		}
	}
	void drawToScanLines(ubyte[][] scanLines)
	{
		//scanLines[0][0..10] = 255;
		//return;
		foreach(i; 0..scanLines.length){
			auto line = scanLines[i];
			foreach(j; 0.._width) {
				writefln("i = %s, j = %s\n", i, j);
				line[4 * j + 2] = clampFloatColor(_pixels[i * _width * 3 + j * 3]);
				line[4 * j + 1] = clampFloatColor(_pixels[i * _width * 3 + j * 3 + 1]);
				line[4 * j + 0] = clampFloatColor(_pixels[i * _width * 3 + j * 3 + 2]);
				line[4 * j + 3] = clampFloatColor(_alphas[j]);
			}
			writeln(line.ptr, line);
		}
	}
	Color pixel (uint x, uint y) const
	{
		auto baseOffset = y * _width * 3 + x * 3;
		return Color(_pixels[baseOffset], _pixels[baseOffset + 1], _pixels[baseOffset + 2]);
	}
	float opacityAt(uint x, uint y)
	{
		return _alphas[y * _width + x];
	}
	void setColorAt(uint x, uint y, Color c) {
		_pixels[y * _width * 3 + x * 3] = c.r;
		_pixels[y * _width * 3 + x * 3 + 1] = c.g;
		_pixels[y * _width * 3 + x * 3 + 2] = c.b;
	}
	void setPixelOpacityAt(uint x, uint y, float op)
	{
		_alphas[y * _width + x] = op;
	}
	void setOpacity(float op)
	{
		_opacity = op;
	}
	void fill(Color c)
	{
		float[3] c1 = [c.r, c.g, c.b];
		foreach(i; 0..width*height)
			_pixels[3 * i..3 * i + 3] = c1;
	}
	void fill(Color c, float opacity)
	{
		fill(c);
		fillPixelOpacity(opacity);
	}
	void fillPixelOpacity(float opacity)
	{
		_alphas[] = opacity;
	}
	void resize(int topExpand, int leftExpand,
	            int bottomExpand, int rightExpand,
	            Color extraSpaceFill = Color.init, float opacity = 0)
	{
		auto newWidth = (_width + topExpand + bottomExpand);
		auto newHeight = (_height + leftExpand + rightExpand);
		auto newPixels = new float[3 * newWidth * newHeight];
		auto newAlphas = new float[newWidth * newHeight];
		// FIXME: speedup
		if (extraSpaceFill != Color.init && topExpand > 0 && leftExpand > 0 &&
		    bottomExpand > 0 && rightExpand > 0) {
			float[3] c1 = extraSpaceFill.asArray();
			newPixels[] = c1;
			newAlphas[] = opacity;
		}
		// FIXME: speedup
		foreach(y; 0.._height) {
			foreach(x; 0.._width) {
				foreach(i; 0..3) {
					newPixels[(y + topExpand) * 3 * newWidth + (x + leftExpand) * 3 + i] =
						_pixels[y * _width * 3 + x * 3 + i];
				}
			}
		}
	}
	const @property uint width() { return _width; }
	const @property uint height() { return _height; }
	@property CompositionMode mode() { return _mode; }
private:
	uint _width, _height;
	uint _xShift, _yShift;
	CompositionMode _mode;
	float[] _pixels; // of size 3 * width * height
	float[] _alphas;
	float _opacity;
}
