import Chat from './components/Chat';
import './App.css';

function App() {
  return (
    <div className="flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-900 min-h-screen w-full h-full">
      <div className="flex flex-col w-full h-full text-center flex-1">
        <Chat />
      </div>
    </div>
  );
}

export default App;
