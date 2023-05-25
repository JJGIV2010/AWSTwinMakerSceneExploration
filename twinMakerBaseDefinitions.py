import json

class Component:
    def __init__(self, **kwargs):
        self.type: str = kwargs.get('type', 'ModelRef')
        self.uri: str = kwargs.get('uri', f's3://twinmaker-workspace-<your workspace name>-XXXXXXXXX-iad/defaultObject.glb') #Replace with your default object
        self.modelType: str = "GLB"

    def to_json(self):
        return {
            "type": self.type,
            "uri": self.uri,
            "modelType": self.modelType
        }


class Transform:
    def __init__(self, **kwargs):
        self.position: list[float] = kwargs.get('position', [0,0,0])
        self.rotation: list[float] = kwargs.get('rotation', [0,0,0])
        self.scale: list[int] = kwargs.get('scale', [1,1,1])

    def to_json(self):
        return {
            "position": self.position,
            "rotation": self.rotation,
            "scale": self.scale
        }


class Statement:
    def __init__(self, **kwargs):
        self.expression: str = kwargs.get('expression', "alarm_status == 'ACTIVE'")
        targetDict = {
            'ERROR': 'iottwinmaker.common.icon:Error',
            'WARNING': 'iottwinmaker.common.icon:Warning',
            'INFO': 'iottwinmaker.common.icon:Info',
        }
        self.target: str = targetDict[kwargs.get('target', 'ERROR')]

    def to_json(self):
        return {
            "expression": self.expression,
            "target": self.target
        }


class Camera:
    def __init__(self, **kwargs):
        self.name: str = kwargs.get('name', 'testCamera')
        self.transform: Transform = kwargs.get('transform', Transform().to_json())
        self.transformConstraint: json = {}
        self.components: json = {
            "type": "Camera",
            "cameraIndex": kwargs.get('cameraIndex', 0)
        }
        self.properties: json = {}

    def to_json(self):
        return {
            "name": self.name,
            "transform": self.transform,
            "transformConstraint": self.transformConstraint,
            "components": self.components,
            "properties": self.properties
        }


class Tag:
    def __init__(self, **kwargs):
        self.name: str = kwargs.get('name', 'testTag')
        self.transform: Transform = kwargs.get('transform', Transform().to_json())
        self.transformConstraint: json = {}
        self.type: str = "Tag"
        self.icon: str = "iottwinmaker.common.icon:Info"
        self.componentType: str = "DataOverlay"
        self.subType: str = "OverlayPanel"
        self.valueDataBindings: list[json] = []
        self.dataRows: list[json] = [
            {
                "rowType": "Markdown",
                "content": kwargs.get('content', 'testContent')
            }
        ]
        self.properties: json = {}

    def to_json(self):
        return {
            "name": self.name,
            "transform": self.transform,
            "transformConstraint": self.transformConstraint,
            "components": [
                {
                    "type": self.type,
                    "icon": self.icon},
                    {
                        "type": self.componentType,
                        "subType": self.subType,
                        "valueDataBindings": self.valueDataBindings,
                        "dataRows": self.dataRows

                    }

            ],
            "properties": self.properties
        }


class Rule:
    def __init__(self, **kwargs):
        self.name: str = kwargs.get('name', 'testRule')
        self.statements: list[Statement] = kwargs.get('statements', [Statement().to_json()])

    def to_json(self):
        return {
            self.name: {
                "statements": self.statements
                }
            }


class Node:
    def __init__(self, **kwargs):
        self.name: str = kwargs.get('name', 'testNode')
        self.transform: Transform = kwargs.get('transform',Transform().to_json())
        self.transformConstraint: json = {}

        # children is a list of indexes of other nodes
        self.children: list = kwargs.get('children', [])
        self.childIndexes: list[int] = kwargs.get('childIndexes', [])
        self.components: list = kwargs.get('components', [])
        self.properties: json = kwargs.get('properties', {})

    def addChild(self, child):
        self.children.append(child)

    def childCount(self):
        return len(self.children)

    def addComponent(self, **kwargs):
        self.components.append(Component(**kwargs).to_json())


    def to_json(self):
        return {
            "name": self.name,
            "transform": self.transform,
            "transformConstraint": self.transformConstraint,
            "children": self.childIndexes,
            "components": self.components,
            "properties": self.properties
        }


class MotionIndicator(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type: str = "MotionIndicator"
        self.shape: str = "LinearPlane"
        self.valueDataBindings: json = {"foregroundColor":{}}
        self.config: json = {
            "numOfRepeatInY": kwargs.get('numOfRepeatInY', 1),
            "defaultSpeed": kwargs.get('defaultSpeed', 1),
            "defaultForegroundColor": kwargs.get('defaultForegroundColor', "#7ed321"),
        }

    def to_json(self):
        return {
            "name": self.name,
            "transform": self.transform,
            "transformConstraint": self.transformConstraint,
            "components": [{
            "type": self.type,
            "shape": self.shape,
            "valueDataBindings": self.valueDataBindings,
            "config": self.config
        }],
        "properties": self.properties
        }


class Scene:
    def __init__(self, **kwargs):
        self.specVersion: str = "1.0"
        self.version: str = "1"
        self.unit: str = "meters"
        self.properties: json = {
            "environmentPreset": "neutral",
            "componentSettings": {
                "Tag": {
                    "autoRescale": False,
                    "scale": 1
                }
            }
        }
        self.nodes: list = kwargs.get('nodes', [])
        self.rootNodeIndexes: list[int] = kwargs.get('rootNodeIndexes', [])
        self.cameras: list[json] = kwargs.get('cameras', [])
        self.rules: json = kwargs.get('rules', Rule().to_json())

    def addNode(self, **kwargs):
        node_index = len(self.nodes)  # Get the index of the added node
        node = kwargs.get('node', Node().to_json())
        self.nodes.append(node.to_json())
        self.rootNodeIndexes.append(node_index)
        if node.children:
            for child in range(len(node.children)):
                self.nodes.append(node.children[child].to_json())
                node.childIndexes.append(len(self.nodes) - 1)

    def addMotionIndicator(self, **kwargs):
        """
        Adds a motion indicator to the scene
        :param motionIndicator:
        :type motionIndicator: MotionIndicator
        Need to work on this one a bit more for cases when someone might want to add it
        as a child of another node
        """
        node_index = len(self.nodes)  # Get the index of the added node
        self.nodes.append(kwargs.get('motionIndicator', MotionIndicator().to_json()))
        self.rootNodeIndexes.append(node_index)

    def getNodeIndex(self, node):
        return self.nodes.index(node.to_json())

    def addRootNodeIndex(self, index):
        self.rootNodeIndexes.append(index)

    def addCamera(self, **kwargs):
        self.cameras.append(Camera(**kwargs).to_json())

    def addTag(self, **kwargs):
        self.nodes.append(Tag(**kwargs).to_json())

    def addRule(self, **kwargs):
        self.rules.update(Rule(**kwargs).to_json())

    def to_json(self):
        return {
            "specVersion": self.specVersion,
            "version": self.version,
            "unit": self.unit,
            "properties": self.properties,
            "nodes": self.nodes,
            "rootNodeIndexes": self.rootNodeIndexes,
            "cameras": self.cameras,
            "rules": self.rules
        }

    def testScene(self):
        self.addNode()
        self.addTag()
        self.addMotionIndicator()
        self.addRule()
        self.addCamera()
        return self.to_json()

