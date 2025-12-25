import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, Send, Upload, Code2, Github, Rocket } from "lucide-react";
import { useState } from "react";
import Chat from "@/components/Chat";
import ProgressDisplay from "@/components/ProgressDisplay";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:7777";

export default function Home() {
  const [activeTab, setActiveTab] = useState("agent");
  const [agentPrompt, setAgentPrompt] = useState("");
  const [agentLoading, setAgentLoading] = useState(false);
  const [agentResults, setAgentResults] = useState<any>(null);
  const [browseUrl, setBrowseUrl] = useState("");
  const [browseLoading, setBrowseLoading] = useState(false);
  const [browseResult, setBrowseResult] = useState<any>(null);
  const [pythonCode, setPythonCode] = useState('print("Hello World")');
  const [pythonLoading, setPythonLoading] = useState(false);
  const [pythonResult, setPythonResult] = useState<any>(null);

  const handleAgentSubmit = async () => {
    if (!agentPrompt.trim()) return;
    
    setAgentLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/agent`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: agentPrompt })
      });
      const data = await response.json();
      setAgentResults(data);
    } catch (error) {
      setAgentResults({ error: String(error) });
    } finally {
      setAgentLoading(false);
    }
  };

  const handleBrowse = async () => {
    if (!browseUrl.trim()) return;
    
    setBrowseLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/browse`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: browseUrl })
      });
      const data = await response.json();
      setBrowseResult(data);
    } catch (error) {
      setBrowseResult({ error: String(error) });
    } finally {
      setBrowseLoading(false);
    }
  };

  const handleExecutePython = async () => {
    if (!pythonCode.trim()) return;
    
    setPythonLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/execute/python`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: pythonCode })
      });
      const data = await response.json();
      setPythonResult(data);
    } catch (error) {
      setPythonResult({ error: String(error) });
    } finally {
      setPythonLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="container mx-auto py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">🤖 AgenticSeek</h1>
          <p className="text-slate-400">自立型 AI エージェント - 自然言語で自動化タスク実行</p>
        </div>

        {/* Main Content */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-8 mb-6 bg-slate-800 border border-slate-700">
            <TabsTrigger value="agent" className="text-xs sm:text-sm">🤖 Agent</TabsTrigger>
            <TabsTrigger value="chat" className="text-xs sm:text-sm">💬 Chat</TabsTrigger>
            <TabsTrigger value="progress" className="text-xs sm:text-sm">📊 Progress</TabsTrigger>
            <TabsTrigger value="browse" className="text-xs sm:text-sm">🌐 Browser</TabsTrigger>
            <TabsTrigger value="files" className="text-xs sm:text-sm">📁 Files</TabsTrigger>
            <TabsTrigger value="code" className="text-xs sm:text-sm">⚙️ Code</TabsTrigger>
            <TabsTrigger value="github" className="text-xs sm:text-sm">🔗 GitHub</TabsTrigger>
            <TabsTrigger value="deploy" className="text-xs sm:text-sm">🚀 Deploy</TabsTrigger>
          </TabsList>

          {/* Agent Tab */}
          <TabsContent value="agent">
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">🤖 AI Agent</CardTitle>
                <CardDescription className="text-slate-400">自然言語でタスクを指示してください</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Textarea
                    placeholder="例: Google にアクセスして、スクリーンショットを取得してから、Python で 'Hello World' を出力してください"
                    value={agentPrompt}
                    onChange={(e) => setAgentPrompt(e.target.value)}
                    className="bg-slate-700 border-slate-600 text-white placeholder-slate-500"
                    rows={4}
                  />
                </div>
                <Button
                  onClick={handleAgentSubmit}
                  disabled={agentLoading || !agentPrompt.trim()}
                  className="w-full bg-blue-600 hover:bg-blue-700"
                >
                  {agentLoading ? <Loader2 className="animate-spin mr-2" /> : <Send className="mr-2" />}
                  実行
                </Button>

                {agentResults && (
                  <div className="mt-6 space-y-4">
                    <div className="bg-slate-700 rounded-lg p-4">
                      <h3 className="text-white font-semibold mb-2">📋 実行計画</h3>
                      <div className="space-y-2">
                        {agentResults.plan?.map((task: string, idx: number) => (
                          <div key={idx} className="text-slate-300 text-sm">• {task}</div>
                        ))}
                      </div>
                    </div>

                    <div className="bg-slate-700 rounded-lg p-4">
                      <h3 className="text-white font-semibold mb-2">✅ 実行結果</h3>
                      <div className="space-y-2 max-h-96 overflow-y-auto">
                        {agentResults.results?.map((result: any, idx: number) => (
                          <div key={idx} className="text-slate-300 text-sm bg-slate-600 p-2 rounded">
                            {result.status === "skipped" ? (
                              <span className="text-yellow-400">⏭️ スキップ: {result.task}</span>
                            ) : result.error ? (
                              <span className="text-red-400">❌ エラー: {result.error}</span>
                            ) : result.stdout ? (
                              <span className="text-green-400">✅ 出力: {result.stdout}</span>
                            ) : (
                              <span className="text-blue-400">📸 スクリーンショット取得完了</span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Chat Tab */}
          <TabsContent value="chat">
            <Card className="bg-slate-800 border-slate-700 h-[600px]">
              <Chat apiBaseUrl={API_BASE_URL} />
            </Card>
          </TabsContent>

          {/* Progress Tab */}
          <TabsContent value="progress">
            <ProgressDisplay apiBaseUrl={API_BASE_URL} />
          </TabsContent>

          {/* Browser Tab */}
          <TabsContent value="browse">
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">🌐 Browser Automation</CardTitle>
                <CardDescription className="text-slate-400">URL を入力してブラウザを自動操作</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Input
                  placeholder="https://www.google.com"
                  value={browseUrl}
                  onChange={(e) => setBrowseUrl(e.target.value)}
                  className="bg-slate-700 border-slate-600 text-white placeholder-slate-500"
                />
                <Button
                  onClick={handleBrowse}
                  disabled={browseLoading || !browseUrl.trim()}
                  className="w-full bg-blue-600 hover:bg-blue-700"
                >
                  {browseLoading ? <Loader2 className="animate-spin mr-2" /> : "アクセス"}
                </Button>

                {browseResult && (
                  <div className="mt-6 space-y-4">
                    {browseResult.error ? (
                      <div className="text-red-400 text-sm">エラー: {browseResult.error}</div>
                    ) : (
                      <>
                        <div className="text-slate-300">
                          <strong>タイトル:</strong> {browseResult.title}
                        </div>
                        {browseResult.screenshot && (
                          <img
                            src={`data:image/png;base64,${browseResult.screenshot}`}
                            alt="Screenshot"
                            className="w-full rounded-lg border border-slate-600"
                          />
                        )}
                      </>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Files Tab */}
          <TabsContent value="files">
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">📁 File Operations</CardTitle>
                <CardDescription className="text-slate-400">ファイルをドラッグ&ドロップしてください</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="border-2 border-dashed border-slate-600 rounded-lg p-8 text-center">
                  <Upload className="mx-auto mb-4 text-slate-400" size={32} />
                  <p className="text-slate-400">ファイルをドラッグ&ドロップ</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Code Tab */}
          <TabsContent value="code">
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">⚙️ Code Executor</CardTitle>
                <CardDescription className="text-slate-400">Python コードを実行</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Textarea
                  value={pythonCode}
                  onChange={(e) => setPythonCode(e.target.value)}
                  className="bg-slate-700 border-slate-600 text-white font-mono"
                  rows={6}
                />
                <Button
                  onClick={handleExecutePython}
                  disabled={pythonLoading || !pythonCode.trim()}
                  className="w-full bg-blue-600 hover:bg-blue-700"
                >
                  {pythonLoading ? <Loader2 className="animate-spin mr-2" /> : <Code2 className="mr-2" />}
                  実行
                </Button>

                {pythonResult && (
                  <div className="mt-6 space-y-2">
                    {pythonResult.stderr && (
                      <div className="bg-red-900 text-red-200 p-3 rounded text-sm">
                        <strong>エラー:</strong> {pythonResult.stderr}
                      </div>
                    )}
                    {pythonResult.stdout && (
                      <div className="bg-green-900 text-green-200 p-3 rounded text-sm">
                        <strong>出力:</strong> {pythonResult.stdout}
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* GitHub Tab */}
          <TabsContent value="github">
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">🔗 GitHub Integration</CardTitle>
                <CardDescription className="text-slate-400">GitHub リポジトリを接続</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-slate-400">GitHub 連携機能は準備中です</p>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Deploy Tab */}
          <TabsContent value="deploy">
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">🚀 Deploy to Production</CardTitle>
                <CardDescription className="text-slate-400">本番環境にデプロイ</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button className="w-full bg-blue-600 hover:bg-blue-700">
                  <Rocket className="mr-2" />
                  Netlify にデプロイ
                </Button>
                <Button className="w-full bg-cyan-600 hover:bg-cyan-700">
                  <Rocket className="mr-2" />
                  Vercel にデプロイ
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
