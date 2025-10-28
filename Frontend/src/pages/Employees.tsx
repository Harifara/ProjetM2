import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ExportButton } from '@/components/exports/ExportButton';
import { useToast } from '@/hooks/use-toast';
import { 
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { 
  Plus, 
  Search, 
  Edit, 
  Trash2, 
  Mail, 
  Phone,
  MapPin
} from 'lucide-react';

interface Employee {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  position: string;
  department: string;
  salary: number;
  status: 'active' | 'inactive';
  hireDate: string;
  address: string;
}

const Employees = () => {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const { toast } = useToast();

  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      // Mock data for demo
      const mockEmployees: Employee[] = [
        {
          id: '1',
          firstName: 'Marie',
          lastName: 'Dupont',
          email: 'marie.dupont@ecart.com',
          phone: '06 12 34 56 78',
          position: 'Développeuse Frontend',
          department: 'IT',
          salary: 45000,
          status: 'active',
          hireDate: '2023-01-15',
          address: 'Paris, France',
        },
        {
          id: '2',
          firstName: 'Jean',
          lastName: 'Martin',
          email: 'jean.martin@ecart.com',
          phone: '06 98 76 54 32',
          position: 'Chef de projet',
          department: 'Management',
          salary: 55000,
          status: 'active',
          hireDate: '2022-06-10',
          address: 'Lyon, France',
        },
        {
          id: '3',
          firstName: 'Sarah',
          lastName: 'Johnson',
          email: 'sarah.johnson@ecart.com',
          phone: '06 11 22 33 44',
          position: 'Designer UX/UI',
          department: 'Design',
          salary: 42000,
          status: 'inactive',
          hireDate: '2023-03-20',
          address: 'Marseille, France',
        },
      ];

      setTimeout(() => {
        setEmployees(mockEmployees);
        setLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Failed to fetch employees:', error);
      toast({
        title: "Erreur",
        description: "Impossible de charger la liste des employés",
        variant: "destructive",
      });
      setLoading(false);
    }
  };

  const handleAddEmployee = () => {
    toast({
      title: "Ajouter un employé",
      description: "Fonctionnalité à implémenter",
    });
  };

  const handleEditEmployee = (employee: Employee) => {
    toast({
      title: "Modifier l'employé",
      description: `Modification de ${employee.firstName} ${employee.lastName}`,
    });
  };

  const handleDeleteEmployee = (employee: Employee) => {
    toast({
      title: "Supprimer l'employé",
      description: `Suppression de ${employee.firstName} ${employee.lastName}`,
      variant: "destructive",
    });
  };

  const filteredEmployees = employees.filter(employee =>
    `${employee.firstName} ${employee.lastName} ${employee.email} ${employee.department}`
      .toLowerCase()
      .includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">Gestion des Employés</h1>
        </div>
        <Card>
          <CardContent className="p-6">
            <div className="animate-pulse space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-12 bg-muted rounded" />
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-foreground">Gestion des Employés</h1>
        <div className="flex items-center space-x-2">
          <ExportButton 
            endpoint="employees" 
            filename="employes" 
            data={filteredEmployees}
          />
          <Button onClick={handleAddEmployee}>
            <Plus className="w-4 h-4 mr-2" />
            Ajouter un employé
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Liste des Employés</CardTitle>
          <CardDescription>
            Gérez les informations de vos employés
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input
                placeholder="Rechercher un employé..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          <div className="rounded-lg border overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nom complet</TableHead>
                  <TableHead>Contact</TableHead>
                  <TableHead>Poste</TableHead>
                  <TableHead>Département</TableHead>
                  <TableHead>Salaire</TableHead>
                  <TableHead>Statut</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredEmployees.map((employee) => (
                  <TableRow key={employee.id}>
                    <TableCell>
                      <div>
                        <p className="font-medium text-foreground">
                          {employee.firstName} {employee.lastName}
                        </p>
                        <p className="text-sm text-muted-foreground flex items-center mt-1">
                          <MapPin className="w-3 h-3 mr-1" />
                          {employee.address}
                        </p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        <p className="text-sm flex items-center">
                          <Mail className="w-3 h-3 mr-2" />
                          {employee.email}
                        </p>
                        <p className="text-sm flex items-center">
                          <Phone className="w-3 h-3 mr-2" />
                          {employee.phone}
                        </p>
                      </div>
                    </TableCell>
                    <TableCell className="font-medium">
                      {employee.position}
                    </TableCell>
                    <TableCell>
                      <Badge variant="secondary">
                        {employee.department}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-medium">
                      {employee.salary.toLocaleString('fr-FR')} €
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant={employee.status === 'active' ? 'default' : 'secondary'}
                        className={employee.status === 'active' ? 'bg-success text-success-foreground' : ''}
                      >
                        {employee.status === 'active' ? 'Actif' : 'Inactif'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleEditEmployee(employee)}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleDeleteEmployee(employee)}
                          className="text-destructive hover:text-destructive"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {filteredEmployees.length === 0 && (
            <div className="text-center py-8">
              <p className="text-muted-foreground">Aucun employé trouvé</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Employees;