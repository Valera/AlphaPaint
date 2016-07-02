module nodes;

import std.stdio;
import std.variant;
import std.exception;
import std.typecons;

// TODO: change to chanel data
enum NodeData {
    Int,
    Double,
    String,
    Mask,
    Image,
    Color,
    MaskOrImage,
    PaintingLayer,
    Curve01,
};

struct NodeInput {
    NodeData inputType;
    string inputName;
}

struct NodeOutput {
    NodeData outputType;
    string outputName;
}

class Node {
    NodeInput[] inputNodes;
    NodeOutput[] outputNodes;
    this () {
    }
};

interface NodeI {
    bool connectionsAreValid(Variant[] nodes);
    bool apply(Variant[] nodes);
}

class Image {}

class Canvas {}


// TODO: value node

/*                                                Color
 *                                                  V
 * TODO: implement simple Curve01 -> RoundMask -> Colored -> SetAlphaMask -> FinalApply
 *                           ^                                     ^              ^
 *                        Pressure     -> Curve01     ->       RoundMask        (x, y)
 */

/* Storage for dynamic brush algorithm and caches */
interface GeneralBrush {
    string settings();
    void setSettings();
    void updateCache();
}

alias float[4] Color;

class DubParameters {
    Color color;
    float x;
    float y;
    float size;
    float pressure;
}

class NodeMap {
private:
    NodeI[] _nodes;
    uint _finalNodeIdx;
    alias NodeAndPort = Tuple!(NodeI, string);
    NodeAndPort[string][uint] incomingConnections;
public:
    Image makeDub(DubParameters params) {
        auto finalNode = _nodes[_finalNodeIdx];
        auto res = cast(Image) finalNode.apply(params);
        enforce(res);
        return res;
    }
    void connect(uint outgoingNodeIndex, string outputId, NodeI incomingNode, string inputId) {
        incomingConnections[outgoingNodeIndex][outputId] = tuple(incomingNode, inputId);

        assert(false);
    }
    


}

class Brush {
private:
    NodeMap _nodeMap;
    float[string] settings;
public:
    this(NodeMap nodeMap) {
        _nodeMap = nodeMap;
    }
    void applyToCanvas(float x, float y, float pressure, Canvas canvas) {
        immutable halfSize = settings["size"] / 2.0;
        canvas.drawImage(x - halfSize, y - halfSize, _nodeMap.makeDub(settings, pressure));
    }
}

class BlendImagesNode : Node {

}

class ColorTransformNode : Node {
    this () {
        super();
        inputNodes ~= NodeInput(NodeData.Color, "color in");
        outputNodes ~= NodeOutput(NodeData.Color, "color out");
    }
}

class Curve01Node : Node {
    this () {
        super();
        outputNodes ~= NodeOutput(NodeData.Curve01, "curve");
    }
}

class RoundPictureNode : Node {
    this () {
        super();
        inputNodes ~= NodeInput(NodeData.Int, "size");
        outputNodes ~= NodeOutput(NodeData.Mask, "mask");
    }
}

class ApplyColorNode : Node {
    this () {
        super();
        inputNodes ~= [NodeInput(NodeData.Mask, "mask"),
                       NodeInput(NodeData.Color, "color")];
        outputNodes ~= NodeOutput(NodeData.Image, "image");
    }
}

class SetAlphaNode: Node {
    this () {
        super();
        inputNodes ~= [
            NodeInput(NodeData.Int, "size"),
            NodeInput(NodeData.MaskOrImage, "mask or image")
        ];
        outputNodes ~= NodeOutput(NodeData.Mask, "mask");
    }
}

class FinalApplyImageNode: Node {
    this () {
        super();
        inputNodes ~= [NodeInput(NodeData.PaintingLayer, "layer"),
                        NodeInput(NodeData.Image, "image"),
                        NodeInput(NodeData.Double, "alpha")];
        outputNodes ~= NodeOutput(NodeData.Mask, "mask");
    }
}

class FormulaNode : Node {
    this (string formula) {
        super();
        inputNodes ~= [
            NodeInput(NodeData.String, "formula"),
            NodeInput(NodeData.Double, "x")
        ];
        outputNodes ~= NodeOutput(NodeData.Double, "y");
    }
}

class RotateNode : Node {
    this () {
        super();
        inputNodes ~= [
            NodeInput(NodeData.Double, "angle"),
            NodeInput(NodeData.MaskOrImage, "mask or image")
        ];
        outputNodes ~= NodeOutput(NodeData.MaskOrImage, "y");
    }
}

void main()
{
    writeln("Ok");
}
