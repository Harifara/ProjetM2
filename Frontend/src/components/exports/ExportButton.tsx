import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger 
} from '@/components/ui/dropdown-menu';
import { Download, FileSpreadsheet, FileText } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface ExportButtonProps {
  endpoint?: string;
  filename?: string;
  data?: any;
  className?: string;
}

export const ExportButton: React.FC<ExportButtonProps> = ({ 
  endpoint, 
  filename = 'export', 
  data,
  className 
}) => {
  const [isExporting, setIsExporting] = useState(false);
  const { toast } = useToast();

  const handleExport = async (format: 'pdf' | 'excel') => {
    setIsExporting(true);
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/v1/exports/${endpoint}/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          format,
          data,
        }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `${filename}.${format === 'excel' ? 'xlsx' : 'pdf'}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        toast({
          title: "Export réussi",
          description: `Le fichier ${format.toUpperCase()} a été téléchargé avec succès.`,
        });
      } else {
        throw new Error('Export failed');
      }
    } catch (error) {
      console.error('Export error:', error);
      toast({
        title: "Erreur d'export",
        description: "Impossible de générer le fichier. Veuillez réessayer.",
        variant: "destructive",
      });
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button 
          variant="outline" 
          size="sm" 
          disabled={isExporting}
          className={className}
        >
          <Download className="w-4 h-4 mr-2" />
          {isExporting ? 'Export...' : 'Exporter'}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => handleExport('pdf')}>
          <FileText className="w-4 h-4 mr-2" />
          PDF
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleExport('excel')}>
          <FileSpreadsheet className="w-4 h-4 mr-2" />
          Excel
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};