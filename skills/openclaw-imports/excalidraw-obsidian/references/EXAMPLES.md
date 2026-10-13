# Excalidraw-Obsidian Skill Examples

## Example 1: Simple Architecture Diagram

```json
{
  "elements": [
    {"type": "cameraUpdate", "width": 800, "height": 600, "x": 0, "y": 0},
    {"type": "rectangle", "id": "client", "x": 50, "y": 250, "width": 150, "height": 80,
     "backgroundColor": "#a5d8ff", "strokeColor": "#4a9eed", "strokeWidth": 2,
     "label": {"text": "Client\n(Web/Mobile)", "fontSize": 16}},
    {"type": "rectangle", "id": "lb", "x": 280, "y": 250, "width": 150, "height": 80,
     "backgroundColor": "#ffd8a8", "strokeColor": "#f59e0b", "strokeWidth": 2,
     "label": {"text": "Load Balancer", "fontSize": 16}},
    {"type": "rectangle", "id": "api1", "x": 500, "y": 150, "width": 140, "height": 70,
     "backgroundColor": "#b2f2bb", "strokeColor": "#22c55e", "strokeWidth": 2,
     "label": {"text": "API Server 1", "fontSize": 14}},
    {"type": "rectangle", "id": "api2", "x": 500, "y": 250, "width": 140, "height": 70,
     "backgroundColor": "#b2f2bb", "strokeColor": "#22c55e", "strokeWidth": 2,
     "label": {"text": "API Server 2", "fontSize": 14}},
    {"type": "rectangle", "id": "api3", "x": 500, "y": 350, "width": 140, "height": 70,
     "backgroundColor": "#b2f2bb", "strokeColor": "#22c55e", "strokeWidth": 2,
     "label": {"text": "API Server 3", "fontSize": 14}},
    {"type": "rectangle", "id": "db", "x": 720, "y": 250, "width": 150, "height": 80,
     "backgroundColor": "#ffc9c9", "strokeColor": "#ef4444", "strokeWidth": 2,
     "label": {"text": "Database\n(PostgreSQL)", "fontSize": 16}},
    {"type": "arrow", "id": "a1", "x": 200, "y": 290, "width": 80, "height": 0,
     "points": [[0,0],[80,0]], "strokeColor": "#1e1e1e", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "arrow", "id": "a2", "x": 430, "y": 290, "width": 70, "height": 0,
     "points": [[0,0],[70,0]], "strokeColor": "#1e1e1e", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "arrow", "id": "a3", "x": 640, "y": 290, "width": 80, "height": 0,
     "points": [[0,0],[80,0]], "strokeColor": "#1e1e1e", "strokeWidth": 2, "endArrowhead": "arrow"}
  ]
}
```

## Example 2: Data Flow Diagram

```json
{
  "elements": [
    {"type": "cameraUpdate", "width": 1000, "height": 700, "x": 0, "y": 0},
    {"type": "text", "id": "title", "x": 350, "y": 30, "text": "Data Flow Architecture", "fontSize": 24, "fontWeight": "bold"},
    
    {"type": "ellipse", "id": "user", "x": 50, "y": 300, "width": 100, "height": 100,
     "backgroundColor": "#a5d8ff", "strokeColor": "#4a9eed", "strokeWidth": 2,
     "label": {"text": "User", "fontSize": 18}},
    
    {"type": "rectangle", "id": "frontend", "x": 200, "y": 320, "width": 140, "height": 60,
     "backgroundColor": "#d0bfff", "strokeColor": "#8b5cf6", "strokeWidth": 2,
     "label": {"text": "Frontend\n(React)", "fontSize": 14}},
    
    {"type": "rectangle", "id": "backend", "x": 400, "y": 320, "width": 140, "height": 60,
     "backgroundColor": "#ffd8a8", "strokeColor": "#f59e0b", "strokeWidth": 2,
     "label": {"text": "Backend\n(Node.js)", "fontSize": 14}},
    
    {"type": "rectangle", "id": "cache", "x": 600, "y": 200, "width": 120, "height": 60,
     "backgroundColor": "#fff3bf", "strokeColor": "#f59e0b", "strokeWidth": 2,
     "label": {"text": "Cache\n(Redis)", "fontSize": 14}},
    
    {"type": "rectangle", "id": "database", "x": 600, "y": 320, "width": 120, "height": 60,
     "backgroundColor": "#ffc9c9", "strokeColor": "#ef4444", "strokeWidth": 2,
     "label": {"text": "Database", "fontSize": 14}},
    
    {"type": "rectangle", "id": "queue", "x": 600, "y": 440, "width": 120, "height": 60,
     "backgroundColor": "#b2f2bb", "strokeColor": "#22c55e", "strokeWidth": 2,
     "label": {"text": "Queue\n(Kafka)", "fontSize": 14}},
    
    {"type": "rectangle", "id": "worker", "x": 780, "y": 440, "width": 120, "height": 60,
     "backgroundColor": "#eebefa", "strokeColor": "#ec4899", "strokeWidth": 2,
     "label": {"text": "Worker", "fontSize": 14}},
    
    {"type": "arrow", "id": "f1", "x": 150, "y": 350, "width": 50, "height": 0,
     "points": [[0,0],[50,0]], "endArrowhead": "arrow", "strokeWidth": 2},
    {"type": "arrow", "id": "f2", "x": 340, "y": 350, "width": 60, "height": 0,
     "points": [[0,0],[60,0]], "endArrowhead": "arrow", "strokeWidth": 2},
    {"type": "arrow", "id": "f3", "x": 540, "y": 350, "width": 60, "height": 0,
     "points": [[0,0],[60,0]], "endArrowhead": "arrow", "strokeWidth": 2},
    {"type": "arrow", "id": "f4", "x": 540, "y": 330, "width": 0, "height": -60,
     "points": [[0,0],[0,-60]], "endArrowhead": "arrow", "strokeWidth": 2},
    {"type": "arrow", "id": "f5", "x": 540, "y": 370, "width": 0, "height": 60,
     "points": [[0,0],[0,60]], "endArrowhead": "arrow", "strokeWidth": 2},
    {"type": "arrow", "id": "f6", "x": 720, "y": 470, "width": 60, "height": 0,
     "points": [[0,0],[60,0]], "endArrowhead": "arrow", "strokeWidth": 2},
    {"type": "arrow", "id": "f7", "x": 660, "y": 440, "width": 0, "height": -160,
     "points": [[0,0],[0,-160]], "endArrowhead": "arrow", "strokeWidth": 2, "strokeStyle": "dashed"}
  ]
}
```

## Example 3: Sequence Diagram

```json
{
  "elements": [
    {"type": "cameraUpdate", "width": 900, "height": 600, "x": 0, "y": 0},
    {"type": "text", "id": "title", "x": 300, "y": 20, "text": "Authentication Sequence", "fontSize": 22, "fontWeight": "bold"},
    
    {"type": "rectangle", "id": "userHead", "x": 50, "y": 60, "width": 100, "height": 40,
     "backgroundColor": "#a5d8ff", "strokeColor": "#4a9eed", "strokeWidth": 2,
     "label": {"text": "User", "fontSize": 16}},
    {"type": "arrow", "id": "userLine", "x": 100, "y": 100, "width": 0, "height": 400,
     "points": [[0,0],[0,400]], "strokeStyle": "dashed", "strokeColor": "#b0b0b0"},
    
    {"type": "rectangle", "id": "appHead", "x": 250, "y": 60, "width": 120, "height": 40,
     "backgroundColor": "#b2f2bb", "strokeColor": "#22c55e", "strokeWidth": 2,
     "label": {"text": "Frontend App", "fontSize": 16}},
    {"type": "arrow", "id": "appLine", "x": 310, "y": 100, "width": 0, "height": 400,
     "points": [[0,0],[0,400]], "strokeStyle": "dashed", "strokeColor": "#b0b0b0"},
    
    {"type": "rectangle", "id": "apiHead", "x": 470, "y": 60, "width": 120, "height": 40,
     "backgroundColor": "#ffd8a8", "strokeColor": "#f59e0b", "strokeWidth": 2,
     "label": {"text": "API Gateway", "fontSize": 16}},
    {"type": "arrow", "id": "apiLine", "x": 530, "y": 100, "width": 0, "height": 400,
     "points": [[0,0],[0,400]], "strokeStyle": "dashed", "strokeColor": "#b0b0b0"},
    
    {"type": "rectangle", "id": "authHead", "x": 690, "y": 60, "width": 120, "height": 40,
     "backgroundColor": "#d0bfff", "strokeColor": "#8b5cf6", "strokeWidth": 2,
     "label": {"text": "Auth Service", "fontSize": 16}},
    {"type": "arrow", "id": "authLine", "x": 750, "y": 100, "width": 0, "height": 400,
     "points": [[0,0],[0,400]], "strokeStyle": "dashed", "strokeColor": "#b0b0b0"},
    
    {"type": "arrow", "id": "msg1", "x": 100, "y": 160, "width": 210, "height": 0,
     "points": [[0,0],[210,0]], "endArrowhead": "arrow", "strokeWidth": 2,
     "label": {"text": "Enter credentials", "fontSize": 13}},
    
    {"type": "arrow", "id": "msg2", "x": 310, "y": 210, "width": 220, "height": 0,
     "points": [[0,0],[220,0]], "endArrowhead": "arrow", "strokeWidth": 2,
     "label": {"text": "POST /auth/login", "fontSize": 13}},
    
    {"type": "arrow", "id": "msg3", "x": 530, "y": 260, "width": 220, "height": 0,
     "points": [[0,0],[220,0]], "endArrowhead": "arrow", "strokeWidth": 2,
     "label": {"text": "Validate user", "fontSize": 13}},
    
    {"type": "arrow", "id": "msg4", "x": 750, "y": 310, "width": -440, "height": 0,
     "points": [[0,0],[-440,0]], "endArrowhead": "arrow", "strokeWidth": 2, "strokeStyle": "dashed",
     "label": {"text": "JWT token", "fontSize": 13}},
    
    {"type": "arrow", "id": "msg5", "x": 530, "y": 360, "width": -220, "height": 0,
     "points": [[0,0],[-220,0]], "endArrowhead": "arrow", "strokeWidth": 2, "strokeStyle": "dashed",
     "label": {"text": "200 OK + token", "fontSize": 13}},
    
    {"type": "arrow", "id": "msg6", "x": 310, "y": 410, "width": -210, "height": 0,
     "points": [[0,0],[-210,0]], "endArrowhead": "arrow", "strokeWidth": 2, "strokeStyle": "dashed",
     "label": {"text": "Store token", "fontSize": 13}},
    
    {"type": "rectangle", "id": "note1", "x": 320, "y": 450, "width": 200, "height": 40,
     "backgroundColor": "#fff3bf", "strokeColor": "#f59e0b", "strokeWidth": 1, "opacity": 50,
     "label": {"text": "Token stored in localStorage", "fontSize": 13}}
  ]
}
```

## Example 4: Mind Map

```json
{
  "elements": [
    {"type": "cameraUpdate", "width": 1000, "height": 700, "x": 0, "y": 0},
    {"type": "text", "id": "title", "x": 350, "y": 20, "text": "System Design Mind Map", "fontSize": 24, "fontWeight": "bold"},
    
    {"type": "ellipse", "id": "central", "x": 400, "y": 300, "width": 200, "height": 100,
     "backgroundColor": "#d0bfff", "strokeColor": "#8b5cf6", "strokeWidth": 3,
     "label": {"text": "System Design", "fontSize": 20, "fontWeight": "bold"}},
    
    {"type": "ellipse", "id": "branch1", "x": 50, "y": 150, "width": 160, "height": 80,
     "backgroundColor": "#a5d8ff", "strokeColor": "#4a9eed", "strokeWidth": 2,
     "label": {"text": "Scalability", "fontSize": 16}},
    {"type": "ellipse", "id": "branch2", "x": 750, "y": 150, "width": 160, "height": 80,
     "backgroundColor": "#b2f2bb", "strokeColor": "#22c55e", "strokeWidth": 2,
     "label": {"text": "Reliability", "fontSize": 16}},
    {"type": "ellipse", "id": "branch3", "x": 50, "y": 450, "width": 160, "height": 80,
     "backgroundColor": "#ffd8a8", "strokeColor": "#f59e0b", "strokeWidth": 2,
     "label": {"text": "Security", "fontSize": 16}},
    {"type": "ellipse", "id": "branch4", "x": 750, "y": 450, "width": 160, "height": 80,
     "backgroundColor": "#ffc9c9", "strokeColor": "#ef4444", "strokeWidth": 2,
     "label": {"text": "Performance", "fontSize": 16}},
    
    {"type": "ellipse", "id": "sub1", "x": 50, "y": 50, "width": 120, "height": 60,
     "backgroundColor": "#e3f2fd", "strokeColor": "#1976d2", "strokeWidth": 1,
     "label": {"text": "Load Balancing", "fontSize": 14}},
    {"type": "ellipse", "id": "sub2", "x": 200, "y": 100, "width": 120, "height": 60,
     "backgroundColor": "#e3f2fd", "strokeColor": "#1976d2", "strokeWidth": 1,
     "label": {"text": "Caching", "fontSize": 14}},
    {"type": "ellipse", "id": "sub3", "x": 850, "y": 50, "width": 120, "height": 60,
     "backgroundColor": "#e8f5e9", "strokeColor": "#2e7d32", "strokeWidth": 1,
     "label": {"text": "Redundancy", "fontSize": 14}},
    {"type": "ellipse", "id": "sub4", "x": 50, "y": 580, "width": 120, "height": 60,
     "backgroundColor": "#fff3e0", "strokeColor": "#ef6c00", "strokeWidth": 1,
     "label": {"text": "Auth", "fontSize": 14}},
    {"type": "ellipse", "id": "sub5", "x": 850, "y": 580, "width": 120, "height": 60,
     "backgroundColor": "#ffebee", "strokeColor": "#c62828", "strokeWidth": 1,
     "label": {"text": "Optimization", "fontSize": 14}},
    
    {"type": "arrow", "id": "line1", "x": 400, "y": 300, "width": 0, "height": 0,
     "points": [[0,0],[-250,-100]], "strokeWidth": 3, "strokeColor": "#8b5cf6"},
    {"type": "arrow", "id": "line2", "x": 400, "y": 300, "width": 0, "height": 0,
     "points": [[0,0],[250,-100]], "strokeWidth": 3, "strokeColor": "#8b5cf6"},
    {"type": "arrow", "id": "line3", "x": 400, "y": 300, "width": 0, "height": 0,
     "points": [[0,0],[-250,100]], "strokeWidth": 3, "strokeColor": "#8b5cf6"},
    {"type": "arrow", "id": "line4", "x": 400, "y": 300, "width": 0, "height": 0,
     "points": [[0,0],[250,100]], "strokeWidth": 3, "strokeColor": "#8b5cf6"},
    
    {"type": "arrow", "id": "line5", "x": 130, "y": 190, "width": 0, "height": 0,
     "points": [[0,0],[-50,-80]], "strokeWidth": 2, "strokeColor": "#4a9eed"},
    {"type": "arrow", "id": "line6", "x": 130, "y": 190, "width": 0, "height": 0,
     "points": [[0,0],[50,-50]], "strokeWidth": 2, "strokeColor": "#4a9eed"},
    {"type": "arrow", "id": "line7", "x": 830, "y": 190, "width": 0, "height": 0,
     "points": [[0,0],[50,-80]], "strokeWidth": 2, "strokeColor": "#22c55e"},
    {"type": "arrow", "id": "line8", "x": 130, "y": 490, "width": 0, "height": 0,
     "points": [[0,0],[-50,50]], "strokeWidth": 2, "strokeColor": "#f59e0b"},
    {"type": "arrow", "id": "line9", "x": 830, "y": 490, "width": 0, "height": 0,
     "points": [[0,0],[50,50]], "strokeWidth": 2, "strokeColor": "#ef4444"}
  ]
}
```

## Example 5: C4 Context Diagram

```json
{
  "elements": [
    {"type": "cameraUpdate", "width": 1000, "height": 700, "x": 0, "y": 0},
    {"type": "text", "id": "title", "x": 350, "y": 30, "text": "C4 Context: E-Commerce System", "fontSize": 24, "fontWeight": "bold"},
    
    {"type": "rectangle", "id": "system", "x": 350, "y": 250, "width": 300, "height": 200,
     "backgroundColor": "#1168bd", "strokeColor": "#0d4f8f", "strokeWidth": 3, "roundness": {"type": 3},
     "label": {"text": "E-Commerce Platform\n\n[Software System]\n\nOnline shopping platform\nwith product catalog,\ncart, and checkout", "fontSize": 14, "fontFamily": 3}},
    
    {"type": "ellipse", "id": "customer", "x": 50, "y": 300, "width": 140, "height": 140,
     "backgroundColor": "#084298", "strokeColor": "#052d5c", "strokeWidth": 2,
     "label": {"text": "Customer\n\n[Person]\n\nShops on the platform", "fontSize": 14, "fontFamily": 3}},
    
    {"type": "ellipse", "id": "admin", "x": 800, "y": 300, "width": 140, "height": 140,
     "backgroundColor": "#084298", "strokeColor": "#052d5c", "strokeWidth": 2,
     "label": {"text": "Administrator\n\n[Person]\n\nManages products\nand orders", "fontSize": 14, "fontFamily": 3}},
    
    {"type": "rectangle", "id": "payment", "x": 350, "y": 50, "width": 300, "height": 120,
     "backgroundColor": "#999999", "strokeColor": "#666666", "strokeWidth": 2, "roundness": {"type": 3},
     "label": {"text": "Payment Gateway\n\n[External System]\n\nProcesses credit card\npayments", "fontSize": 14, "fontFamily": 3}},
    
    {"type": "rectangle", "id": "email", "x": 350, "y": 530, "width": 300, "height": 120,
     "backgroundColor": "#999999", "strokeColor": "#666666", "strokeWidth": 2, "roundness": {"type": 3},
     "label": {"text": "Email Service\n\n[External System]\n\nSends order\nconfirmations", "fontSize": 14, "fontFamily": 3}},
    
    {"type": "arrow", "id": "r1", "x": 190, "y": 350, "width": 160, "height": 0,
     "points": [[0,0],[160,0]], "endArrowhead": "arrow", "strokeWidth": 2, "strokeColor": "#000000",
     "label": {"text": "Browses products\nAdds to cart\nPlaces orders", "fontSize": 12}},
    
    {"type": "arrow", "id": "r2", "x": 650, "y": 350, "width": 150, "height": 0,
     "points": [[0,0],[150,0]], "endArrowhead": "arrow", "strokeWidth": 2, "strokeColor": "#000000",
     "label": {"text": "Manages catalog\nViews orders\nUpdates inventory", "fontSize": 12}},
    
    {"type": "arrow", "id": "r3", "x": 500, "y": 250, "width": 0, "height": -80,
     "points": [[0,0],[0,-80]], "endArrowhead": "arrow", "strokeWidth": 2, "strokeColor": "#000000",
     "label": {"text": "Processes payments", "fontSize": 12}},
    
    {"type": "arrow", "id": "r4", "x": 500, "y": 450, "width": 0, "height": 80,
     "points": [[0,0],[0,80]], "endArrowhead": "arrow", "strokeWidth": 2, "strokeColor": "#000000",
     "label": {"text": "Sends notifications", "fontSize": 12}}
  ]
}
```
