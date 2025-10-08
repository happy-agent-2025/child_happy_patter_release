import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
// 由于当前项目没有Redux store，我们暂时注释掉这些导入
// import { selectCurrentCanvas, setCurrentCanvas } from '../../store/slices/canvasSlice';
// import { generateStory } from '../../store/slices/storySlice';

// 定义CanvasElement接口
interface CanvasElement {
  id: string;
  type: 'character' | 'animal' | 'plant' | 'building' | 'natural' | 'object';
  name: string;
  position: { x: number; y: number };
  size: { width: number; height: number };
}

const CameraCapture = () => {
    const dispatch = useDispatch();
    const navigate = useNavigate();
    // 由于当前项目没有Redux store，我们使用模拟数据
    // const currentCanvas = useSelector(selectCurrentCanvas);
    const currentCanvas = {
      id: 'mock-canvas-id',
      name: 'captured-image.jpg',
      elements: [
        { id: '1', type: 'character', name: 'person', position: { x: 100, y: 100 }, size: { width: 50, height: 50 } },
        { id: '2', type: 'plant', name: 'tree', position: { x: 200, y: 150 }, size: { width: 60, height: 80 } }
      ]
    };

    // 处理画作元素点击事件
    const handleElementClick = (element: CanvasElement) => {
        console.log('Element clicked:', element);
        // 可以在这里添加更多逻辑，比如选中元素后更新属性面板
    };

    // 处理生成故事按钮点击事件
    const handleGenerateStory = () => {
        if (currentCanvas) {
            // 模拟生成故事并导航到故事页面
            console.log('Generating story for canvas:', currentCanvas.id);
            // 模拟异步操作
            setTimeout(() => {
                // 生成成功后导航到故事页面
                navigate(`/story/${currentCanvas.id}`);
            }, 1000);
        } else {
            console.warn('没有选中的画布');
        }
    };

    return (
        <div className="camera-capture-container">
            {/* 左侧工具栏 */}
            <div className="toolbar">
                <button onClick={() => console.log('Save')}>保存</button>
                <button onClick={handleGenerateStory}>生成故事</button>
                <ul>
                    <li onClick={() => handleElementClick({ id: '1', type: 'character', name: 'person', position: { x: 0, y: 0 }, size: { width: 50, height: 50 } })}>
                        <img src="https://placehold.co/50x50" alt="person" />
                        person
                    </li>
                    <li onClick={() => handleElementClick({ id: '2', type: 'plant', name: 'tree', position: { x: 0, y: 0 }, size: { width: 50, height: 50 } })}>
                        <img src="https://placehold.co/50x50" alt="tree" />
                        tree
                    </li>
                    <li onClick={() => handleElementClick({ id: '3', type: 'building', name: 'house', position: { x: 0, y: 0 }, size: { width: 50, height: 50 } })}>
                        <img src="https://placehold.co/50x50" alt="house" />
                        house
                    </li>
                    <li onClick={() => handleElementClick({ id: '4', type: 'object', name: 'car', position: { x: 0, y: 0 }, size: { width: 50, height: 50 } })}>
                        <img src="https://placehold.co/50x50" alt="car" />
                        car
                    </li>
                </ul>
            </div>

            {/* 中间画布区域 */}
            <div className="canvas-area">
                <h3>{currentCanvas?.name || 'captured-image.jpg'}</h3>
                <div className="canvas" style={{ background: '#ADD8E6' }}>
                    {/* 渲染画作元素 */}
                    {currentCanvas?.elements.map((element) => (
                        <div
                            key={element.id}
                            style={{
                                position: 'absolute',
                                left: `${element.position.x}px`,
                                top: `${element.position.y}px`,
                                width: `${element.size.width}px`,
                                height: `${element.size.height}px`
                            }}
                        >
                            <img src={`https://placehold.co/${element.size.width}x${element.size.height}`} alt={element.name} />
                        </div>
                    ))}
                </div>
            </div>

            {/* 右侧属性面板 */}
            <div className="property-panel">
                <h3>属性面板</h3>
                <div>
                    <label>基本信息</label>
                    <input placeholder="元素名称" />
                </div>
                <div>
                    <label>动作设置</label>
                    <select>
                        <option value="walk">行走</option>
                        {/* 更多动作选项 */}
                    </select>
                    <input type="number" placeholder="动画时长 (秒)" defaultValue="1" />
                </div>
                <div>
                    <label>位置设置</label>
                    {/* 更多位置设置选项 */}
                </div>
            </div>
        </div>
    );
};

export default CameraCapture;