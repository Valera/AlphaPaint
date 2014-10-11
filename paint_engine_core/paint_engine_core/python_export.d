module python_export;

import engine;
import brush;
import pyd.pyd;

//void hello_func() {
//	writefln("Hello, world!");
//}


extern (C) void PydMain() {
//	def	!(hello_func)();
	module_init();
	wrap_class!(
		Image,
		Init!(uint, uint),
		Def!(Image.printHello),
		Def!(Image.width),
		Def!(Image.height),
		Def!(Image.registerQImageScanLines),
		Def!(Image.register1),
		Def!(Image.register2),
		Def!(Image.startPaintTransaction),
	)();
	wrap_class!(
		BrushStroke,
		Init!(SimpleBrush, Image, Color),
		Def!(BrushStroke.processMouseMove),
		Def!(BrushStroke.reset)
	)();
	wrap_class!(
		SimpleBrush,
		Init!(float, SimpleBrush.Type, float, float)
	)();
	wrap_struct!(
		Color,
		Init!(float, float, float)
	)();
	wrap_struct!(
		Rect
		)();
}
