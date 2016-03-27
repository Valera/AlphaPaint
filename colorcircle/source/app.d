module app;

import std.stdio;
import dlangui;
import colorcircle;

mixin APP_ENTRY_POINT;

// version = bug;

extern (C) int UIAppMain(string[] args) {
    Window window = Platform.instance.createWindow("test", null);

    auto w = new ColorCircle("colorcircle");
    //w.padding = Rect(40, 40, 40, 40);
    version (bug) {
        auto vl = new VerticalLayout();
        vl.addChild(w);
    }

    //w.mouseEvent = delegate bool(Widget w1, MouseEvent e) { w.points ~= [e.x, e.y]; return true; };

    version (bug) {
        window.mainWidget = vl;
    } else {
        window.mainWidget = w;
    }
    window.show();
    return Platform.instance.enterMessageLoop();
}

