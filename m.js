import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  CircularProgress,
  Box,
  TablePagination,
  Button,
  TextField,
  IconButton,
  Tooltip,
  Snackbar,
  Alert
} from '@mui/material';
import { Save, Edit, Close, Check } from '@mui/icons-material';

const DataTable = ({ tableName }) => {
  const [tableData, setTableData] = useState([]);
  const [originalData, setOriginalData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [editingCell, setEditingCell] = useState(null); // Changed from editingId to editingCell
  const [changedRows, setChangedRows] = useState(new Set());
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    const fetchTableData = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/table/${tableName}`, {
          headers: {
            Authorization: 'Bearer dummy-token'
          }
        });

        const data = response.data?.data ?? response.data ?? [];
        setTableData(data);
        setOriginalData(JSON.parse(JSON.stringify(data)));
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch table data: ' + err.message);
        setLoading(false);
      }
    };

    fetchTableData();
  }, [tableName]);

  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Edit specific cell instead of entire row
  const handleEditCell = (rowId, fieldName) => {
    setEditingCell({ rowId, fieldName });
  };

  // Cancel editing specific cell
  const handleCancelEdit = (rowId, fieldName) => {
    // Revert changes for this specific field if it was modified
    if (changedRows.has(rowId)) {
      const originalRow = originalData.find(row => row.id === rowId);
      setTableData(prev => prev.map(row =>
        row.id === rowId ? { ...row, [fieldName]: originalRow[fieldName] } : row
      ));
      
      // Check if row still has changes after reverting this field
      const updatedRow = { ...tableData.find(row => row.id === rowId), [fieldName]: originalRow[fieldName] };
      const originalRow2 = originalData.find(row => row.id === rowId);
      
      if (JSON.stringify(originalRow2) === JSON.stringify(updatedRow)) {
        setChangedRows(prev => {
          const newSet = new Set(prev);
          newSet.delete(rowId);
          return newSet;
        });
      }
    }
    setEditingCell(null);
  };

  // Save specific cell
  const handleSaveCell = () => {
    setEditingCell(null);
  };

  const handleFieldChange = (id, field, value) => {
    const updatedData = tableData.map(item =>
      item.id === id ? { ...item, [field]: value } : item
    );
    setTableData(updatedData);

    // Track changed rows
    const originalItem = originalData.find(item => item.id === id);
    const currentItem = updatedData.find(item => item.id === id);

    if (JSON.stringify(originalItem) !== JSON.stringify(currentItem)) {
      setChangedRows(prev => new Set(prev).add(id));
    } else {
      setChangedRows(prev => {
        const newSet = new Set(prev);
        newSet.delete(id);
        return newSet;
      });
    }
  };

  const handleSaveChanges = async () => {
    try {
      const changes = Array.from(changedRows).map(id => {
        const currentItem = tableData.find(item => item.id === id);
        const originalItem = originalData.find(item => item.id === id);
        return { id, ...currentItem };
      });

      if (changes.length === 0) {
        showSnackbar('No changes to save', 'warning');
        return;
      }

      await axios.put(
        `http://localhost:5000/table/${tableName}/bulk-update`,
        changes,
        { headers: { Authorization: 'Bearer dummy-token' } }
      );

      // Update original data
      setOriginalData(JSON.parse(JSON.stringify(tableData)));
      setChangedRows(new Set());
      setEditingCell(null);
      showSnackbar(`${changes.length} records updated successfully`);
    } catch (err) {
      setError('Failed to save changes: ' + err.message);
      showSnackbar('Failed to save changes', 'error');
    }
  };

  if (loading) return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
      <CircularProgress />
    </Box>
  );

  if (error) return (
    <Typography color="error" variant="body1" sx={{ p: 2 }}>
      {error}
    </Typography>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Data for: {tableName}
        </Typography>

        <Button
          variant="contained"
          color="primary"
          onClick={handleSaveChanges}
          disabled={changedRows.size === 0}
        >
          Submit Changes ({changedRows.size})
        </Button>
      </Box>

      {Array.isArray(tableData) && tableData.length > 0 ? (
        <Paper elevation={3} sx={{ overflow: 'hidden' }}>
          <TableContainer sx={{ maxHeight: 'calc(100vh - 200px)', maxWidth: '100%' }}>
            <Table stickyHeader aria-label="sticky table">
              <TableHead>
                <TableRow>
                  {Object.keys(tableData[0]).map((col, idx) => (
                    <TableCell
                      key={idx}
                      sx={{
                        fontWeight: 'bold',
                        backgroundColor: 'primary.main',
                        color: 'primary.contrastText'
                      }}
                    >
                      {col}
                    </TableCell>
                  ))}
                  <TableCell
                    sx={{
                      fontWeight: 'bold',
                      backgroundColor: 'primary.main',
                      color: 'primary.contrastText'
                    }}
                  >
                    Actions
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {tableData
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((row) => (
                    <TableRow
                      key={row.id}
                      hover
                      sx={{
                        '&:nth-of-type(even)': { backgroundColor: 'action.hover' },
                        ...(changedRows.has(row.id) && { backgroundColor: '#fffde7' })
                      }}
                    >
                      {Object.keys(row).map((key) => {
                        const isEditing = editingCell?.rowId === row.id && editingCell?.fieldName === key;
                        const isIdField = key === 'id';
                        
                        return (
                          <TableCell key={`${row.id}-${key}`}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              {isEditing ? (
                                <>
                                  <TextField
                                    value={row[key] !== null && row[key] !== undefined ? String(row[key]) : ''}
                                    onChange={(e) => handleFieldChange(row.id, key, e.target.value)}
                                    size="small"
                                    variant="outlined"
                                    sx={{ flex: 1 }}
                                  />
                                  <IconButton size="small" onClick={handleSaveCell}>
                                    <Check color="primary" />
                                  </IconButton>
                                  <IconButton size="small" onClick={() => handleCancelEdit(row.id, key)}>
                                    <Close color="error" />
                                  </IconButton>
                                </>
                              ) : (
                                <>
                                  <Box sx={{ flex: 1 }}>
                                    {row[key] !== null && row[key] !== undefined ? String(row[key]) : 'NULL'}
                                  </Box>
                                  {!isIdField && (
                                    <IconButton
                                      size="small"
                                      onClick={() => handleEditCell(row.id, key)}
                                      disabled={editingCell !== null}
                                    >
                                      <Edit color={changedRows.has(row.id) ? "primary" : "action"} />
                                    </IconButton>
                                  )}
                                </>
                              )}
                            </Box>
                          </TableCell>
                        );
                      })}
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {changedRows.has(row.id) ? 'Modified' : 'Unchanged'}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))
                }
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            rowsPerPageOptions={[5, 10, 25, 50]}
            component="div"
            count={tableData.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </Paper>
      ) : (
        <Typography variant="body1" color="text.secondary">
          No data available in this table.
        </Typography>
      )}

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default DataTable;