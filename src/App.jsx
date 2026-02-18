import { VideoEngine } from './components/VideoEngine'
import { START_NODE_ID } from './config/nodes'

function App() {
  return <VideoEngine startNodeId={START_NODE_ID} />
}

export default App
