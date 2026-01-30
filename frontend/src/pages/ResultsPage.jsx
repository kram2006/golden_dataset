import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Download, FileJson, Image as ImageIcon, RefreshCw } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ResultsPage = () => {
  const { toast } = useToast();
  const [datasets, setDatasets] = useState([]);
  const [screenshots, setScreenshots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedImage, setSelectedImage] = useState(null);

  useEffect(() => {
    loadResults();
  }, []);

  const loadResults = async () => {
    try {
      setLoading(true);
      const [datasetsRes, screenshotsRes] = await Promise.all([
        axios.get(`${API}/automation/datasets`),
        axios.get(`${API}/automation/screenshots`)
      ]);

      setDatasets(datasetsRes.data.datasets || []);
      setScreenshots(screenshotsRes.data.screenshots || []);
    } catch (error) {
      console.error('Error loading results:', error);
      toast({
        title: 'Error',
        description: 'Failed to load results',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const downloadDataset = async (model, filename) => {
    try {
      const response = await axios.get(`${API}/automation/datasets/${model}/${filename}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast({
        title: 'Success',
        description: 'Dataset downloaded successfully',
      });
    } catch (error) {
      console.error('Error downloading dataset:', error);
      toast({
        title: 'Error',
        description: 'Failed to download dataset',
        variant: 'destructive'
      });
    }
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading results...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold">Results</h1>
          <p className="text-gray-600">View and download generated datasets and screenshots</p>
        </div>
        <Button onClick={loadResults} variant="outline">
          <RefreshCw className="mr-2 h-4 w-4" /> Refresh
        </Button>
      </div>

      <Tabs defaultValue="datasets" className="space-y-4">
        <TabsList className="grid w-full max-w-md grid-cols-2">
          <TabsTrigger value="datasets">
            <FileJson className="mr-2 h-4 w-4" />
            Datasets ({datasets.length})
          </TabsTrigger>
          <TabsTrigger value="screenshots">
            <ImageIcon className="mr-2 h-4 w-4" />
            Screenshots ({screenshots.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="datasets">
          {datasets.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center text-gray-500">
                No datasets generated yet. Run automation to generate datasets.
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {datasets.map((dataset, i) => (
                <Card key={i} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="text-base flex items-center gap-2">
                      <FileJson className="h-4 w-4" />
                      {dataset.filename}
                    </CardTitle>
                    <CardDescription>
                      <div className="space-y-1 text-xs">
                        <div>Model: <Badge variant="outline">{dataset.model}</Badge></div>
                        <div>Task: <Badge variant="outline">{dataset.task_id}</Badge></div>
                      </div>
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="text-xs text-gray-600">
                        <div>Size: {formatBytes(dataset.size_bytes)}</div>
                        <div>Created: {new Date(dataset.timestamp).toLocaleString()}</div>
                      </div>
                      <Button
                        size="sm"
                        className="w-full"
                        onClick={() => downloadDataset(dataset.model, dataset.filename)}
                      >
                        <Download className="mr-2 h-3 w-3" /> Download
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="screenshots">
          {screenshots.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center text-gray-500">
                No screenshots captured yet. Run automation to capture screenshots.
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {screenshots.map((screenshot, i) => (
                <Card
                  key={i}
                  className="hover:shadow-lg transition-shadow cursor-pointer"
                  onClick={() => setSelectedImage(screenshot)}
                >
                  <CardContent className="p-2">
                    <img
                      src={`${BACKEND_URL}${screenshot.url}`}
                      alt={screenshot.filename}
                      className="w-full h-32 object-cover rounded-md mb-2"
                    />
                    <div className="space-y-1">
                      <div className="text-xs font-medium truncate">{screenshot.filename}</div>
                      <div className="flex gap-1 flex-wrap">
                        <Badge variant="outline" className="text-xs">{screenshot.task_id}</Badge>
                        <Badge variant="outline" className="text-xs">{screenshot.type}</Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Image Modal */}
      {selectedImage && (
        <div
          className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedImage(null)}
        >
          <div className="max-w-4xl max-h-full" onClick={(e) => e.stopPropagation()}>
            <img
              src={`${BACKEND_URL}${selectedImage.url}`}
              alt={selectedImage.filename}
              className="max-w-full max-h-[90vh] rounded-lg"
            />
            <div className="mt-4 text-white text-center">
              <p className="font-medium">{selectedImage.filename}</p>
              <Button
                variant="outline"
                className="mt-2"
                onClick={() => setSelectedImage(null)}
              >
                Close
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultsPage;
