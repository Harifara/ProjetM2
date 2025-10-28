import { useState, useEffect } from 'react';
import { Plus, Package, AlertTriangle, TrendingUp, TrendingDown } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Skeleton } from '@/components/ui/skeleton';
import { useToast } from '@/hooks/use-toast';
import { stockApi } from '@/lib/api';
import { ExportButton } from '@/components/exports/ExportButton';

interface StockItem {
  id: string;
  name: string;
  sku: string;
  category_name: string;
  warehouse_name: string;
  quantity: number;
  min_threshold: number;
  max_threshold: number;
  is_expired: boolean;
  expiry_date: string | null;
  needs_replenishment: boolean;
}

const Stock = () => {
  const [stockItems, setStockItems] = useState<StockItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const { toast } = useToast();

  useEffect(() => {
    fetchStockItems();
  }, []);

  const fetchStockItems = async () => {
    setIsLoading(true);
    try {
      const data = await stockApi.getStockItems();
      setStockItems(data);
    } catch (error) {
      toast({
        title: "Erreur",
        description: "Impossible de charger les articles",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusBadge = (item: StockItem) => {
    if (item.is_expired) return <Badge variant="destructive">Expiré</Badge>;
    if (item.needs_replenishment) return <Badge variant="destructive">Stock Bas</Badge>;
    if (item.quantity >= item.max_threshold) return <Badge className="bg-green-500">Stock Élevé</Badge>;
    return <Badge variant="secondary">Normal</Badge>;
  };

  const filteredItems = stockItems.filter(item =>
    item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.sku.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.category_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const stats = {
    total: stockItems.length,
    lowStock: stockItems.filter(item => item.needs_replenishment).length,
    expired: stockItems.filter(item => item.is_expired).length,
    totalValue: stockItems.reduce((sum, item) => sum + item.quantity, 0),
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-12 w-64" />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-32" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Gestion du Stock</h1>
          <p className="text-muted-foreground">Gérez vos articles et inventaires</p>
        </div>
        <Button className="gap-2">
          <Plus className="h-4 w-4" />
          Ajouter un Article
        </Button>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="shadow-card border-0">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Articles Total</CardTitle>
            <Package className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">{stats.total}</div>
          </CardContent>
        </Card>

        <Card className="shadow-card border-0">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Stock Bas</CardTitle>
            <TrendingDown className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">{stats.lowStock}</div>
          </CardContent>
        </Card>

        <Card className="shadow-card border-0">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Articles Expirés</CardTitle>
            <AlertTriangle className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">{stats.expired}</div>
          </CardContent>
        </Card>

        <Card className="shadow-card border-0">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Quantité Totale</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-500">{stats.totalValue}</div>
          </CardContent>
        </Card>
      </div>

      {/* Search and Export */}
      <Card className="shadow-card border-0">
        <CardHeader>
          <div className="flex items-center justify-between gap-4">
            <Input
              placeholder="Rechercher par nom, SKU ou catégorie..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="max-w-md"
            />
            <ExportButton endpoint="/api/stock/items/export/" filename="stock-items" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>SKU</TableHead>
                  <TableHead>Nom</TableHead>
                  <TableHead>Catégorie</TableHead>
                  <TableHead>Magasin</TableHead>
                  <TableHead className="text-right">Quantité</TableHead>
                  <TableHead className="text-right">Seuil Min</TableHead>
                  <TableHead>Statut</TableHead>
                  <TableHead>Date Expiration</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredItems.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center text-muted-foreground py-8">
                      Aucun article trouvé
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredItems.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell className="font-mono text-sm">{item.sku}</TableCell>
                      <TableCell className="font-medium">{item.name}</TableCell>
                      <TableCell>{item.category_name}</TableCell>
                      <TableCell>{item.warehouse_name}</TableCell>
                      <TableCell className="text-right font-semibold">{item.quantity}</TableCell>
                      <TableCell className="text-right text-muted-foreground">{item.min_threshold}</TableCell>
                      <TableCell>{getStatusBadge(item)}</TableCell>
                      <TableCell>
                        {item.expiry_date
                          ? new Date(item.expiry_date).toLocaleDateString('fr-FR')
                          : '-'}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Stock;
