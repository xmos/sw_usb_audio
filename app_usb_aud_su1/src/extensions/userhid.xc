
extern in port p_but;

void UserReadHIDButtons(unsigned char hidData[])
{
    int tmp;
    p_but :> tmp;
    tmp = ~tmp;
    tmp &=3;
    hidData[0] = tmp;
}
