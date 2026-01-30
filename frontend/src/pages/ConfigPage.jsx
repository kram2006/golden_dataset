import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircle2, AlertCircle, Key, Server } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ConfigPage = () => {
  const { toast } = useToast();
  const [config, setConfig] = useState({
    openrouter_api_key: '',
    xo_url: 'http://localhost:8080',
    xo_username: 'admin@admin.net',
    xo_password: 'admin'
  });
  const [hasApiKey, setHasApiKey] = useState(false);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/automation/config`);
      setHasApiKey(response.data.has_api_key);
      setConfig(prev => ({
        ...prev,
        xo_url: response.data.xo_url,
        xo_username: response.data.xo_username
      }));
    } catch (error) {
      console.error('Error loading config:', error);
      toast({
        title: 'Error',
        description: 'Failed to load configuration',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      await axios.post(`${API}/automation/config`, config);
      setHasApiKey(true);
      toast({
        title: 'Success',
        description: 'Configuration saved successfully',
      });
      // Clear password from state after saving
      setConfig(prev => ({ ...prev, openrouter_api_key: '', xo_password: '' }));
    } catch (error) {
      console.error('Error saving config:', error);
      toast({
        title: 'Error',
        description: 'Failed to save configuration',
        variant: 'destructive'
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading configuration...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">Configuration</h1>
        <p className="text-gray-600">Configure your OpenRouter API key and Xen Orchestra settings</p>
      </div>

      {hasApiKey && (
        <Alert className="bg-green-50 border-green-200">
          <CheckCircle2 className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            API key is configured. You can start running automation tasks.
          </AlertDescription>
        </Alert>
      )}

      {!hasApiKey && (
        <Alert className="bg-yellow-50 border-yellow-200">
          <AlertCircle className="h-4 w-4 text-yellow-600" />
          <AlertDescription className="text-yellow-800">
            Please configure your OpenRouter API key to start using the automation system.
          </AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Key className="h-5 w-5" />
            OpenRouter Configuration
          </CardTitle>
          <CardDescription>
            Get your API key from <a href="https://openrouter.ai/keys" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">openrouter.ai/keys</a>
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="api-key">OpenRouter API Key</Label>
            <Input
              id="api-key"
              type="password"
              placeholder="sk-or-..." 
              value={config.openrouter_api_key}
              onChange={(e) => setConfig({ ...config, openrouter_api_key: e.target.value })}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Server className="h-5 w-5" />
            Xen Orchestra Configuration
          </CardTitle>
          <CardDescription>
            Configure connection to your Xen Orchestra instance
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="xo-url">XO URL</Label>
            <Input
              id="xo-url"
              type="url"
              placeholder="http://localhost:8080"
              value={config.xo_url}
              onChange={(e) => setConfig({ ...config, xo_url: e.target.value })}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="xo-username">XO Username</Label>
            <Input
              id="xo-username"
              type="email"
              placeholder="admin@admin.net"
              value={config.xo_username}
              onChange={(e) => setConfig({ ...config, xo_username: e.target.value })}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="xo-password">XO Password</Label>
            <Input
              id="xo-password"
              type="password"
              placeholder="Enter password"
              value={config.xo_password}
              onChange={(e) => setConfig({ ...config, xo_password: e.target.value })}
            />
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end gap-4">
        <Button variant="outline" onClick={loadConfig}>
          Reset
        </Button>
        <Button onClick={handleSave} disabled={saving}>
          {saving ? 'Saving...' : 'Save Configuration'}
        </Button>
      </div>
    </div>
  );
};

export default ConfigPage;
